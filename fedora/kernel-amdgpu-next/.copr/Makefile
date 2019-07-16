srpm:
	dnf --nogpgcheck -y install rpkg --repofrompath=repo,https://copr-be.cloud.fedoraproject.org/results/xxmitsu/mesa-and-llvm-git/srpm-builds
	echo '%dist %{nil}' > ~/.rpmmacros
	git clone git://people.freedesktop.org/~agd5f/linux
	git checkout drm-next
	rpkg srpm --outdir=$(outdir) --spec=$(spec)
