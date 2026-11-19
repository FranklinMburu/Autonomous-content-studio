"""What every plug must provide. A plug turns the standard Shot into its own tool's request."""


class BackendError(Exception):
    """The tool failed for this shot (crash, bad output). The router tries the next one."""


class QuotaExceeded(BackendError):
    """The tool's free allowance is used up for now. The router tries the next one and benches this one."""


class NotAvailable(BackendError):
    """The tool can't run here (no GPU, not installed, switched off, costs money). Not counted as a failure."""


class Backend:
    name = "base"
    free = True            # False = costs money; the router refuses it unless config says enabled AND paid_ok
    needs_gpu = False
    can_text_to_video = True
    can_image_to_video = True

    def available(self):
        """Cheap check, no generation. Raise NotAvailable with the reason, or return None."""

    def generate(self, shot, out_path):
        """Make the clip at out_path (mp4). Raise BackendError / QuotaExceeded on failure."""
        raise NotImplementedError
