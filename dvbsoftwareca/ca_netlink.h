#ifndef __CA_NETLINK_H
#define __CA_NETLINK_H

#include "ca.h"
#include <linux/netlink.h>
#include <net/genetlink.h>
//#include <linux/kernel.h>
#include <linux/version.h>

int reply_ca(struct sk_buff *skb_2, struct genl_info *info);
int netlink_send_cw(unsigned short ca_num, ca_descr_t *ca_descr);
int netlink_send_pid(unsigned short ca_num, ca_pid_t *ca_pid);
int register_netlink(void);
void unregister_netlink(void);

// attributes
enum {
	ATTR_UNSPEC,
	ATTR_CA_SIZE,
	ATTR_CA_NUM,
	ATTR_CA_DESCR,
	ATTR_CA_PID,
        __ATTR_MAX,
};
#define ATTR_MAX (__ATTR_MAX - 1)

// commands
enum {
	CMD_UNSPEC,
	CMD_ASK_CA_SIZE,
	CMD_SET_CW,
	CMD_SET_PID,
	CMD_MAX,
};

extern struct nla_policy ca_policy[ATTR_MAX + 1];
extern struct genl_family ca_family;
extern struct genl_ops ask_ca_size_ops[];
extern int devices_counter;

#endif
