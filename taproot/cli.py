from __future__ import annotations
import subprocess, typer
from rich import print
from . import __version__
from .aws import list_profiles, ensure_credentials, collect_instances
from .cache import load as cache_load, save as cache_save
from .tui import pick_profile, pick_instance, PROFILE_CHANGE

app=typer.Typer(help="Taproot TUI", add_completion=False)

def _ssh(profile:str, iid:str, user:str="root"):
    cmd=["aws","ec2-instance-connect","ssh","--instance-id",iid,"--connection-type","eice","--os-user",user,"--profile",profile]
    print(f"[grey50]$ {' '.join(cmd)}[/grey50]")
    subprocess.run(cmd, check=True)

@app.command()
def connect():
    cache=cache_load(); profile=cache.get("profile")
    while True:
        profile=pick_profile(list_profiles(), profile)
        session=ensure_credentials(profile)
        while True:
            insts=collect_instances(session)
            choice=pick_instance(insts, profile)
            if choice is PROFILE_CHANGE:
                break
            iid=choice["id"]; cache_save(profile,iid); _ssh(profile,iid); return

@app.command()
def version(): print(__version__)

if __name__=="__main__": app()
