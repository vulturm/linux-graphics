# make use of copr srpm to build amdgpu kernel
# Author: Mihai Vultur <xanto at egaming dot ro>
.PHONY: srpm
.ONESHELL:
.SHELLFLAGS := -xc


clone_repo := git://people.freedesktop.org/~agd5f/linux
clone_branch := drm-next


srpm:
	dnf -y install git make rpkg
	git clone --single-branch --branch $(clone_branch) --depth=1 $(clone_repo) $(clone_branch)
	kernel_major=`grep '^VERSION =' $(clone_branch)/Makefile | grep -oP '[0-9]+'`
	kernel_minor=`grep '^PATCHLEVEL =' $(clone_branch)/Makefile | grep -oP '[0-9]+'`

	sed -i "s=@@kernel_version@@=$${kernel_major}=g;s=@@base_sublevel@@=$${kernel_minor}=g" fedora/kernel/kernel-amdgpu-next/kernel.spec
	mv $(clone_branch) linux-$${kernel_major}.$${kernel_minor}
	tar czf $(outdir)/$(clone_branch).tar.gz --exclude .git linux-$${kernel_major}.$${kernel_minor}

	cp fedora/kernel/kernel-amdgpu-next/* $(outdir)
	rpkg srpm --spec fedora/kernel/kernel-amdgpu-next/kernel.spec --with vanilla --outdir $(outdir)
