# Domjudge problem verify tool

## System setup

```bash
$ sudo vim /etc/default/grub
# Change GRUB_CMDLINE_LINUX_DEFAULT to
GRUB_CMDLINE_LINUX_DEFAULT="quiet cgroup_enable=memory swapaccount=1 systemd.unified_cgroup_hierarchy=0"

$ sudo update-grub

$ sudo reboot

$ cat /proc/cmdline
# Check
```

## Install

1. Create `.env`
    ```
    JUDGE0_URL=http://server:2358
    ```
2. `docker compose build`
3. `docker compose up -d`
4. Visit `http://localhost:8501`