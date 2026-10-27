import argparse,getpass
from farmlink.database import init_db,get_session
from farmlink.services.accounts import create_admin
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=["init-db","create-admin"]); args=parser.parse_args(); init_db()
    if args.command=="init-db": print("Database tables initialized."); return
    name=input("Administrator name: ").strip(); email=input("Administrator email: ").strip().lower()
    password=getpass.getpass("Password (minimum 10 characters): "); confirm=getpass.getpass("Confirm password: ")
    if password!=confirm: raise SystemExit("Passwords do not match.")
    with get_session() as db:
        admin=create_admin(db,name,email,password); print(f"Administrator created for {admin.email}.")
if __name__=="__main__": main()
