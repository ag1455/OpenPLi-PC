#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <unistd.h>
#include <sys/select.h>
#include <sys/time.h>
#include <linux/dvb/dmx.h>

#include <iostream>
#include <vector>

/* #define USE_TS_FILTER */

#ifdef USE_TS_FILTER
# define TS_LEN       188
# define TS_SYNC_BYTE 0x47
# define BUFFER_SIZE  (TS_LEN * 2048)
#else
# define BUFFER_SIZE (256 * 1024)
#endif

#ifdef USE_TS_FILTER
int syncTS(unsigned char *buf, int len)
{
	int i = 0;
	for (i = 0; i < len; i++)
	{
		if (buf[i] == TS_SYNC_BYTE)
		{
			if ((i + TS_LEN) < len)
			{
				if (buf[i + TS_LEN] != TS_SYNC_BYTE) continue;
			}
			break;
		}
	}
	return i;
}
#endif

unsigned long timevalToMs(const struct timeval *tv)
{
	return(tv->tv_sec * 1000) + ((tv->tv_usec + 500) / 1000);
}

long deltaTimeMs(struct timeval *tv, struct timeval *last_tv)
{
	return timevalToMs(tv) - timevalToMs(last_tv);
}

int Select(int maxfd, fd_set *readfds, fd_set *writefds, fd_set *exceptfds, struct timeval *timeout)
{
	int retval;
	fd_set rset, wset, xset;
	timeval interval;
	timerclear(&interval);

	/* make a backup of all fd_set's and timeval struct */
	if (readfds) rset = *readfds;
	if (writefds) wset = *writefds;
	if (exceptfds) xset = *exceptfds;
	if (timeout) interval = *timeout;

	while (1)
	{
		retval = select(maxfd, readfds, writefds, exceptfds, timeout);

		if (retval < 0)
		{
			/* restore the backup before we continue */
			if (readfds) *readfds = rset;
			if (writefds) *writefds = wset;
			if (exceptfds) *exceptfds = xset;
			if (timeout) *timeout = interval;
			if (errno == EINTR) continue;
			std::cout << "select failed " << errno << std::endl;
			break;
		}

		break;
	}
	return retval;
}

ssize_t Read(int fd, void *buf, size_t count)
{
	int retval;
	char *ptr = (char*)buf;
	size_t handledcount = 0;
	while (handledcount < count)
	{
		retval = read(fd, &ptr[handledcount], count - handledcount);

		if (retval == 0) return handledcount;
		if (retval < 0)
		{
			if (errno == EINTR) continue;
			std::cout << "read failed " << errno << std::endl;
			return retval;
		}
		handledcount += retval;
	}
	return handledcount;
}

ssize_t NBRead(int fd, void *buf, size_t count)
{
	int retval;
	while (1)
	{
		retval = ::read(fd, buf, count);
		if (retval < 0)
		{
			if (errno == EINTR) continue;
			std::cout << "read failed " << errno << std::endl;
		}
		return retval;
	}
}

int measureBitrate(int adapter, int demux, bool oneshot, std::vector<int> pids)
{
	char filename[128];
	snprintf(filename, 128, "/dev/dvb/adapter%d/demux%d", adapter, demux);
	std::vector<int> fds;
	std::vector<unsigned long long> b_total, b_tot1, min_kb_s, max_kb_s, avg_kb_s, curr_kb_s;
	for (unsigned int i = 0; i < pids.size(); i++)
	{
		int fd = ::open(filename, O_RDONLY);
		::fcntl(fd, F_SETFL, O_NONBLOCK);
		::ioctl(fd, DMX_SET_BUFFER_SIZE, 1024 * 1024);
		dmx_pes_filter_params flt;
#ifdef USE_TS_FILTER
		flt.pes_type = 0; /* officially not allowed, but on systems with ADD_PID support, this results in TS data */
#else
		flt.pes_type = DMX_PES_OTHER; /* PES payload data */
#endif
		flt.pid     = pids[i];
		flt.input   = DMX_IN_FRONTEND;
		flt.output  = DMX_OUT_TAP;
		flt.flags   = DMX_IMMEDIATE_START;
		::ioctl(fd, DMX_SET_PES_FILTER, &flt);
		fds.push_back(fd);

		b_total.push_back(0);
		b_tot1.push_back(0);
		min_kb_s.push_back(50000ULL);
		max_kb_s.push_back(0);
		curr_kb_s.push_back(0);
		avg_kb_s.push_back(0);
	}

	struct timeval first_tv, last_print_tv;

	gettimeofday(&first_tv, 0);
	last_print_tv.tv_sec = first_tv.tv_sec;
	last_print_tv.tv_usec = first_tv.tv_usec;

	while (1)
	{
		unsigned char buf[BUFFER_SIZE];
		int maxfd = 0;
		fd_set rset;
		FD_ZERO(&rset);
		struct timeval timeout;
		timeout.tv_sec = 1;
		timeout.tv_usec = 0;
		for (unsigned int i = 0; i < fds.size(); i++)
		{
			if (fds[i] >= 0) FD_SET(fds[i], &rset);
			if (fds[i] >= maxfd) maxfd = fds[i] + 1;
		}

		int result = Select(maxfd, &rset, NULL, NULL, &timeout);
		if (result <= 0) break;

		for (unsigned int i = 0; i < fds.size(); i++)
		{
			if (fds[i] >= 0 && FD_ISSET(fds[i], &rset))
			{
				int b_len = NBRead(fds[i], buf, sizeof(buf));
				int b_start = 0;
#ifdef USE_TS_FILTER
				if (b_len >= TS_LEN)
				{
					b_start = syncTS(buf, b_len);
				}
				else
				{
					b_len = 0;
				}
#endif
				int b = b_len - b_start;
				if (b <= 0) continue;
				b_total[i] += b;
				b_tot1[i] += b;
			}
		}
		struct timeval tv;
		gettimeofday(&tv, 0);
		int d_print_ms = deltaTimeMs(&tv, &last_print_tv);
		if (d_print_ms >= 1000)
		{
			for (unsigned int i = 0; i < fds.size(); i++)
			{
				int d_tim_ms = deltaTimeMs(&tv, &first_tv);
				avg_kb_s[i] = (b_total[i] * 8ULL) / (unsigned long long)d_tim_ms;
				curr_kb_s[i] = (b_tot1[i] * 8ULL) / (unsigned long long)d_print_ms;
#ifdef USE_TS_FILTER
				/* compensate for TS and PES overhead */
				avg_kb_s[i] = avg_kb_s[i] * 97ULL / 100ULL;
				curr_kb_s[i] = curr_kb_s[i] * 97ULL / 100ULL;
#else
				/* compensate for PES overhead */
				avg_kb_s[i] = avg_kb_s[i] * 99ULL / 100ULL;
				curr_kb_s[i] = curr_kb_s[i] * 99ULL / 100ULL;
#endif
				b_tot1[i] = 0;

				if (curr_kb_s[i] < min_kb_s[i])
				{
					min_kb_s[i] = curr_kb_s[i];
				}
				if (curr_kb_s[i] > max_kb_s[i])
				{
					max_kb_s[i] = curr_kb_s[i];
				}
				last_print_tv.tv_sec = tv.tv_sec;
				last_print_tv.tv_usec = tv.tv_usec;
				if (oneshot)
				{
					std::cout << curr_kb_s[i] << std::endl;
				}
				else
				{
					std::cout << min_kb_s[i] << " " << max_kb_s[i] << " " << avg_kb_s[i] << " " << curr_kb_s[i] << std::endl;
				}
			}
			if (oneshot) break;
		}
	}
}

int main(int argc, char *argv[])
{
	if (argc < 3) exit(-1);
	std::vector<int> pids;
	for (int i = 1; i < argc - 1; i++)
	{
		pids.push_back(atoi(argv[i + 1]));
	}
	measureBitrate(0, atoi(argv[1]), false, pids);
}
