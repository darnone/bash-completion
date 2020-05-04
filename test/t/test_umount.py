import pytest

from conftest import assert_bash_exec


class TestUmount:
    @pytest.fixture(scope="class")
    def dummy_mnt(self, request, bash):
        """
        umount completion from fstab can't be tested directly because it
        (correctly) uses absolute paths. So we create a custom completion which
        reads from a file in our text fixture instead.
        """
        assert_bash_exec(bash, "unset COMPREPLY cur; unset -f _mnt_completion")
        assert_bash_exec(
            bash,
            "_mnt_completion() { "
            "local cur=$(_get_cword); "
            "_linux_fstab $(_get_pword) < mount/test-fstab; "
            "} && complete -F _mnt_completion _mnt",
        )
        request.addfinalizer(
            lambda: assert_bash_exec(
                bash, "complete -r _mnt; unset -f _mnt_completion"
            )
        )

    @pytest.mark.complete("umount ")
    def test_1(self, completion):
        assert completion

    @pytest.mark.complete("_mnt /mnt/nice-test-p")
    def test_mnt_basic(self, completion, dummy_mnt):
        assert completion == "/mnt/nice-test-path"

    # Note in tests below that return only one result, that the result
    # is shell unescaped due to how assert_complete handles the
    # "one result on same line case".

    @pytest.mark.complete(r"_mnt /mnt/nice\ test-p")
    def test_mnt_space(self, completion, dummy_mnt):
        assert completion == r"/mnt/nice test-path"

    @pytest.mark.complete(r"_mnt /mnt/nice\$test-p")
    def test_mnt_dollar(self, completion, dummy_mnt):
        assert completion == "/mnt/nice$test-path"

    @pytest.mark.complete(r"_mnt /mnt/nice\ test\\p")
    def test_mnt_backslash(self, completion, dummy_mnt):
        assert completion == r"/mnt/nice test\path"

    @pytest.mark.complete(r"_mnt /mnt/nice\ ")
    def test_mnt_after_space(self, completion, dummy_mnt):
        assert completion == sorted(
            (r"/mnt/nice\ test\\path", r"/mnt/nice\ test-path")
        )

    @pytest.mark.complete(r"_mnt /mnt/nice\$")
    def test_mnt_at_dollar(self, completion, dummy_mnt):
        assert completion == "/mnt/nice$test-path"

    @pytest.mark.complete(r"_mnt /mnt/nice\'")
    def test_mnt_at_quote(self, completion, dummy_mnt):
        assert completion == "/mnt/nice'test-path"

    @pytest.mark.complete("_mnt /mnt/other")
    def test_mnt_other(self, completion, dummy_mnt):
        assert completion == "/mnt/other'test path"

    @pytest.mark.complete("_mnt -L Ubu")
    def test_mnt_label_space(self, completion, dummy_mnt):
        assert completion == "Ubuntu Karmic"

    @pytest.mark.complete("_mnt -L Deb")
    def test_mnt_label_quote(self, completion, dummy_mnt):
        assert completion == "Debian-it's awesome"
