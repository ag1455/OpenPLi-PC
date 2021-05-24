/*
##############################################################################
#
# Tools to generate the nim_sockets file to use with
# openpliPC.
# source: https://github.com/nobody9/openpliPC
# Forum:  http://openpli.org/forums/topic/20871-build-script-for-openpli-enigma2-on-ubuntu-104-32-bit/
#
# Based on get_fe_info.c from http://http://code.google.com/p/vtuner/
#
##############################################################################
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>


#include <linux/dvb/frontend.h>

#define CNIM_VER "1.1-mod1455"

int PrintHelp () {
	printf ("\nCommand line options:\n \
	Optional:\n \
	-a number of adapter     : provide a numerical value default:4\n \
	-f number of frontend    : provide a numerical default:4\n \
	-o /path/filename        : path and filename default:./nim_sockets\n\
	-h                       : this help\n \
	-d                       : enable debug\n");
}

int main(int argc, char **argv) {
	char *ArrayDVBTunerType[] = { "UNKNOWN","UNKNOWN","UNKNOWN","UNKNOWN","UNKNOWN","UNKNOWN","UNKNOWN","UNKNOWN","UNKNOWN"};
	char **DVBTunerType;
	char NIM_File[254];
	short TunerFound = 0;
	short OutfileOK = 0;
	short Debug = 0;
	int c = -1;
	int FE_Max = 4;
	int Adaptor_Max = 4;
	FILE *outfile;

	extern char *optarg;
	extern int optind, opterr, optopt;

	strcpy (NIM_File, "nim_sockets");

	printf("\nInfo: create_nim_sockets %s started\n\n", CNIM_VER );

	while((c = getopt(argc, argv, "a:f:o:dh")) != -1) {
		switch(c) {
			case 'd': // enable debug
				Debug = 1;
			break;
			case 'h': // help
				PrintHelp();
				return -1;
			break;
			case 'a':
				if (atoi(optarg))
					Adaptor_Max = atoi(optarg);
				else {
					fprintf(stderr, "Error: Invalid parameter for -a should be a number.\n");
					return -1;
				}
			break;
			case 'f':
				if (atoi(optarg))
					FE_Max = atoi(optarg);
				else {
					fprintf(stderr, "Error: Invalid parameter for -f should be a number.\n");
					return -1;
				}
			break;
			case 'o':
				strcpy(NIM_File, optarg);
			break;

			default:
				PrintHelp();
				return -1;
			break;
		}
	}

	if (optind != argc ) {
		fprintf (stderr, "Error: unknow parameter detected [%s].\n", argv[argc-1]);
		PrintHelp();
		return -1;
	}

	if (outfile = fopen(NIM_File, "w"))
		OutfileOK = 1;
	else {
		printf("\nError creating nim_sockets file [%s]\n", NIM_File);
		return -1;
	}

	DVBTunerType = ArrayDVBTunerType;
	int TunerType_S = 0;
	int TunerType_C = 1;
	int TunerType_T = 2;
	DVBTunerType[TunerType_S]="DVB-S";
	DVBTunerType[TunerType_C]="DVB-C";
	DVBTunerType[TunerType_T]="DVB-T";
	/* DVB-S2 is a special case of DVB-S and is tested from frontend capabilities */

	int i=0;
	int j=0;
	int Return_ioctl=0;

	for(i=0; i<Adaptor_Max; ++i) {
		for (j=0; j<FE_Max; ++j) {
			char devstr[80];
			sprintf( devstr, "/dev/dvb/adapter%d/frontend%d", i, j);

			if( access( devstr, F_OK ) != -1 ) {
				//file exists
				int fe_fd = open( devstr, O_RDONLY);
				if(fe_fd>0) {
					struct dvb_frontend_info fe_info;
					Return_ioctl = ioctl(fe_fd, FE_GET_INFO, &fe_info);
					if(Return_ioctl == 0) {
						TunerFound=1;
						printf("Tuner found: %s: %s\n", devstr, fe_info.name);

						if (Debug) {
							printf("// dvb_frontend_info for %s\n", devstr);
							printf("struct dvb_frontend_info FETYPE = {\n");
							printf("  .name                  = \"%s\",\n", fe_info.name);
							printf("  .type                  = %d,\n", fe_info.type);
							printf("  .frequency_min         = %d,\n", fe_info.frequency_min);
							printf("  .frequency_max         = %d,\n", fe_info.frequency_max);
							printf("  .frequency_stepsize    = %d,\n", fe_info.frequency_stepsize);
							printf("  .frequency_tolerance   = %d,\n", fe_info.frequency_tolerance);
							printf("  .symbol_rate_min       = %d,\n", fe_info.symbol_rate_min);
							printf("  .symbol_rate_max       = %d,\n", fe_info.symbol_rate_max);
							printf("  .symbol_rate_tolerance = %d,\n", fe_info.symbol_rate_tolerance);
							printf("  .notifier_delay        = %d,\n", fe_info.notifier_delay);
							printf("  .caps                  = 0x%x\n", fe_info.caps);
							printf("};\n\n");
						}

						/* Nim socket outpout start */
						if (Debug)
							printf("NIM Socket %d:\n", i);
						if (OutfileOK)
							fprintf(outfile, "NIM Socket %d:\n", i);

						/* 2nd generation DVB Tuner detected adding 2 to the TunerType */
						if ((fe_info.caps & FE_CAN_2G_MODULATION) == FE_CAN_2G_MODULATION) {
							if (Debug)
								printf("      Type: %s2\n", DVBTunerType[fe_info.type]);
							if (OutfileOK)
								fprintf(outfile,"      Type: %s2\n", DVBTunerType[fe_info.type]);
						}

						/* 1st generation DVB Tuner */
						else {
							if (Debug)
								printf("      Type: %s\n", DVBTunerType[fe_info.type]);
							if (OutfileOK)
								fprintf(outfile,"      Type: %s\n", DVBTunerType[fe_info.type]);
						}

						if (Debug) {
							printf("      Name: %s\n", fe_info.name);
							printf("      Has_Outputs: no\n");
							printf("      Frontend_Device: %d\n", j);
							printf("\n");
						}
						if (OutfileOK) {
							fprintf(outfile,"      Name: %s\n", fe_info.name);
							fprintf(outfile,"      Has_Outputs: no\n");
							fprintf(outfile,"      Frontend_Device: %d\n", j);
							fprintf(outfile,"\n");
						}
						/* Nim socket output end */
					}
					else
						fprintf(stderr, "Error: ioctl error [%d] for [%s] : ", Return_ioctl, devstr);
				}
				close( fe_fd );
			}
			else {
				/* file doesn't exist */
				if (Debug)
					printf("/dev/dvb/adapter%d/frontend%d doesn\'t exist\n", i, j);
			}
		}
	}

	if (!TunerFound) {
		printf("\n\nError: Unable to find a valid DVB card or vtuner on your system.\n\
		Please fix this problem and run it again.\n");
	}
	if (OutfileOK) {
		fclose(outfile);
		if (TunerFound)
			printf("\nInfo: File [%s] created please check it.\n", NIM_File);
	}

	printf("\nInfo: create_nim_sockets done\n");
}
