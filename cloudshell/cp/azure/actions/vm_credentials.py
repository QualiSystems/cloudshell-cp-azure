import random
import string

from cloudshell.cp.azure.actions.ssh_key_pair import SSHKeyPairActions


class VMCredentialsActions(SSHKeyPairActions):
    DEFAULT_LINUX_USERNAME = "adminuser"
    DEFAULT_WINDOWS_USERNAME = "adminuser"
    LINUX_SSH_KEY_PATH = "/home/{username}/.ssh/authorized_keys"

    def _generate_password(self, length=10):
        """Generate password of the given length with digit and uppercase letter.

        :param int length: password length
        :rtype: str
        """
        password = [random.choice(string.ascii_lowercase) for _ in range(length)]

        # add uppercase and digit symbol to the password
        rand_idxs = random.sample(range(length), 2)

        for idx, symbols_range in zip(
            rand_idxs, [string.ascii_uppercase, string.digits]
        ):
            password[idx] = random.choice(symbols_range)

        return "".join(password)

    def prepare_windows_credentials(self, username, password):
        """Prepare Windows credentials for the VM.

        Generates password, set default user if credentials weren't provided
        :param str username: VM username
        :param str password: VM password
        :return: username and password
        :rtype: tuple[str, str]
        """
        if not username:
            username = self.DEFAULT_WINDOWS_USERNAME
        if not password:
            password = self._generate_password()

        return username, password

    def prepare_linux_credentials(self, username, password):
        """Prepare Linux credentials for the VM.

        Prepare SSH key, set default user if credentials weren't provided
        :param str username: VM username
        :param str password: VM password
        :return: username, password
        :rtype: tuple[str, str]
        """
        if not username:
            username = self.DEFAULT_LINUX_USERNAME

        return username, password

    def prepare_ssh_public_key_path(self, username):
        """Prepare path for the SSH Public key.

        :param str username:
        :rtype: str
        """
        return self.LINUX_SSH_KEY_PATH.format(username=username)
