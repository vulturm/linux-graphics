
config.llvm_tools_dir = '/usr/bin'
config.llvm_shlib_dir = '%(llvm_shlib_dir)s' % lit_config.params

if hasattr(config, 'host_triple'):
    # This means we are running lit regression tests

    # Regression tests write output to this directory, so we need to be able to specify
    # a temp directory when invoking lit. e.g. lit -Dllvm_obj_root=/tmp/lit
    config.llvm_obj_root = "%(llvm_obj_root)s" % lit_config.params
    lit_config.load_config(config, '%(llvm_test_root)s/lit.cfg.py' % lit_config.params)
else:
    # This means we are running lit unit tests

    # For unit tests, llvm_obj_root is used to find the unit test binaries.
    config.llvm_obj_root = '%(llvm_unittest_bindir)s' % lit_config.params
    lit_config.load_config(config, '%(llvm_test_root)s/Unit/lit.cfg.py' % lit_config.params)
