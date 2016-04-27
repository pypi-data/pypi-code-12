import sys, subprocess

def install():
    subprocess.call("bash /usr/local/include PiStorms_install.sh", shell=True)
    
def upgrade():
    subprocess.call("bash /usr/local/include/PiStorms_upgrade.sh", shell=True)
