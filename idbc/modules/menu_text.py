main_options = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, "exit"]

command_options = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

welcome_msg = "[bold red]Welcome to Iroha Renkinjutsu[/bold red]"

menu_text = """
[bold yellow]What Would You Like To Do?:[/bold yellow]

1. Parse Genesis Block to DB [italic green](Iroha Account & Asset Commands)[/italic green]
2. Parse Blocks  
3. Schedule Block Parser
4. Test Iroha Node Connection [italic green](Test if specified Iroha Node can be reached)[/italic green]

Type exit to quit or hit ctrl + c\n"""

commands_menu = """

[bold yellow]-- Account Management--[/bold yellow]

1. Create Account (CreateAccount)
2. Set Account Key/Value Detail (SetAccountDetail)
3. Detach Role from account (DetactRole)
4. Add new role to account (AppendRole)
5. Remove Signatory (rem_sign)
6. Set Account Quorum (set_qrm)
7. Revoke permission from account (revoke_perm)
8. Add Signatory to Account (add_sign)
9. Grant permission over your account (grant_perm)

[bold yellow]-- Asset Management --[/bold yellow]

10. Create Asset (crt_ast)
11. Add Asset Quantity (add_ast_qty)
12. Transfer Assets (tran_ast)
13. Subtract Assets Quantity (sub_ast_qty)

[bold yellow]-- Domain Management--[/bold yellow]

14. Create New Role (crt_role)
15. Create Domain (crt_dmn)

--Network & Peer Management--
16. Add Peer to Iroha Network (add_peer)

[bold red]0. Back to Main Menu (b)[/bold red]

Type exit to quit or hit ctrl + c\n """

query_menu = """
--Accounts--
1. Get all permissions related to role (get_role_perm)
2. Get Transactions by transactions' hashes (get_tx)

--Assets--
3. Get information about asset (get_ast_info)
4. Get Account's Transactions (get_acc_tx)
5. Get Account's Asset Transactions (get_acc_ast_tx)
6. Get all current roles in the system (get_roles)
7. Get Account's Signatories (get_acc_sign)
8. Get Account's Assets (get_acc_ast)
9. Get Account Information (get_acc)
0. Back (b)

Type exit to quit or hit ctrl + c\n """
