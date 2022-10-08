# KERNEL_VERSION	:= `uname -r`
# KERNEL_DIR	:= /lib/modules/$(KERNEL_VERSION)/build
PWD		:= $(shell pwd)

ifeq ($(KERNELRELEASE),)
all: modules

modules:
	$(MAKE) ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) -C $(KSRC) M=$(shell pwd) modules

strip:
	$(CROSS_COMPILE)strip e2-proc.ko --strip-unneeded

clean: $(clean_more)
	rm -fr *.mod.c *.mod *.o .*.cmd *.ko *~ *.a
	rm -fr .tmp_versions
	rm -fr Module.symvers ; rm -fr Module.markers ; rm -fr modules.order
	cd core ; rm -fr *.mod.c *.mod *.o .*.cmd *.ko
	cd hal ; rm -fr *.mod.c *.mod *.o .*.cmd *.ko
	cd os_dep ; rm -fr *.mod.c *.mod *.o .*.cmd *.ko
else
EXTRA_CFLAGS += -Wenum-compare
ccflags-y += -D__CHECK_ENDIAN__

e2_procfs-y := \
	e2_procfs_amode.o \
	e2_procfs_bus.o \
	e2_procfs_denc.o \
	e2_procfs_fileio.o \
	e2_procfs_fp.o \
	e2_procfs_info.o \
	e2_procfs_main.o \
	e2_procfs_progress.o \
	e2_procfs_vmode.o \
	e2_procfs_vmpeg.o \
	e2_procfs_frontend.o
obj-m := \
	e2_procfs.o

CFLAGS_trace.o := -I$(src)

endif
