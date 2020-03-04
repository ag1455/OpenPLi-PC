obj-m := dvbsoftwareca.o
dvbsoftwareca-objs := dvb_softwareca.o ca_netlink.o
KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

default:
	$(MAKE) -C $(KDIR) M=$(PWD) modules
clean:
	rm -f Module.symvers
	rm -f *.o
	rm -f *.ko
	rm -f *.mod.c
	rm -f .*.cmd
	rm -f *.mod
	rm -f *.order
	rm -Rf .tmp_versions
