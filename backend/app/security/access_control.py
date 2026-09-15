"""PAIOS capability-based access control for browser + laptop automation."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import os
import re

class AccessDenied(PermissionError):
    pass

@dataclass
class AccessPolicy:
    browser: bool = True
    app_launch: bool = True
    mouse: bool = True
    keyboard: bool = True
    clipboard: bool = True
    screenshot: bool = True
    filesystem_read: bool = True
    filesystem_write: bool = True
    process_control: bool = False
    shell: bool = False
    destructive: bool = False
    network_download: bool = True
    allowed_apps: set[str] = field(default_factory=lambda: {
        'chrome','edge','firefox','brave','notepad','calculator','calc','vscode',
        'explorer','file explorer','powershell','cmd','terminal','paint','wordpad'
    })
    blocked_paths: tuple[str,...] = ('C:\\Windows','C:\\Program Files','C:\\Program Files (x86)')

class AccessController:
    def __init__(self):
        self.policy=AccessPolicy()
        self._armed=False
        self._one_shot=set()

    def arm(self, capabilities=None):
        self._armed=True
        if capabilities:
            self._one_shot.update(capabilities)

    def disarm(self):
        self._armed=False; self._one_shot.clear()

    @property
    def armed(self): return self._armed

    def _check(self, capability):
        if capability in self._one_shot:
            self._one_shot.discard(capability); return
        if not getattr(self.policy, capability, False):
            raise AccessDenied(f'PAIOS access denied: capability={capability}')

    def authorize(self, capability, *, target=None):
        self._check(capability)
        if capability=='app_launch' and target:
            name=str(target).lower().strip()
            if name not in self.policy.allowed_apps:
                raise AccessDenied(f'Application not allowlisted: {target}')
        if capability in ('filesystem_read','filesystem_write') and target:
            p=self.safe_path(target)
            if capability=='filesystem_write' and not self.policy.destructive and p.exists() and p.is_dir():
                raise AccessDenied('Directory replacement/deletion is disabled.')
        return True

    def safe_path(self, raw):
        p=Path(os.path.expandvars(os.path.expanduser(str(raw)))).resolve()
        blocked=[Path(x).resolve() for x in self.policy.blocked_paths if x]
        for b in blocked:
            try:
                p.relative_to(b); raise AccessDenied(f'Path outside PAIOS safe area: {p}')
            except ValueError: pass
        home=Path.home().resolve()
        # Laptop automation is limited to the user's profile by default.
        try: p.relative_to(home)
        except ValueError: raise AccessDenied(f'Path must be inside user profile: {p}')
        return p

    def authorize_url(self, url):
        self._check('browser')
        if not re.match(r'^https?://', str(url), re.I):
            raise AccessDenied('Only http/https URLs are allowed.')
        return True

access_controller=AccessController()
