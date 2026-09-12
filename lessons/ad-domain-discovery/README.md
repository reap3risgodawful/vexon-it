# Free lesson: “The domain cannot be found”

**A fictional paper exercise by Vexon IT. No installation or purchase required.** Read the ticket and write your decision before viewing the answer. This lesson teaches troubleshooting reasoning; no actual Windows or VM test was performed, and the observations are invented for the exercise. Allow about 10 minutes.

## The concepts in two minutes

AD DS stores identities and computer objects in a domain. A domain controller (DC) answers authentication and directory requests. DNS helps a client find the DC. An organizational unit (OU) groups directory objects for administration and policy scope. A security group expresses membership; it does not grant useful access until a resource or rule assigns that group permissions. A Group Policy Object (GPO) carries settings and needs the correct link, scope and processing conditions to apply.

A local account belongs to one Windows installation. A domain account belongs to the directory. `CLIENT1\alex` and `HELPDESK\alex` can therefore be different identities even if their short names match.

## Ticket LAB-001

“I am joining the new lab client to `helpdesk.test`, but Windows says the domain cannot be found.”

Fictional configuration for a disposable lab, supplied as paper evidence:

| Item | Intended | Observed on client |
|---|---|---|
| Client OS | Windows 11 Pro or Enterprise | Windows 11 Pro |
| Client IPv4 | 172.28.77.20/24 | 172.28.77.20/24 |
| DC/DNS | 172.28.77.10 | DC is running at that address |
| Client DNS server | 172.28.77.10 | 172.28.77.99 |
| Default gateway | None in the private lab | None |
| Virtual switch | AD-HELPDESK-PRIVATE | Same private switch as DC |

The fictional client reports that `Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.helpdesk.test` timed out. A lookup explicitly directed to the intended server — `Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.helpdesk.test -Server 172.28.77.10` — returns a service record naming `LAB-DC1.helpdesk.test`. These are supplied observations, not captured command output. You do not need to run either command.

## Your task

1. Which observation is the strongest lead? Explain why buying a new Windows edition is not the first fix here.
2. What single configuration change would you propose inside the disposable client VM?
3. Name two checks after the change. What result counts as success?
4. Should you change the household router DNS, turn off Windows Firewall, or put the DC on a public network?
5. Draft a four-line ticket note: symptom, evidence, change, result. If you have not actually performed a check, label its result “expected”.

## Sample answer — read after attempting

Given the supplied configuration, the client resolver `172.28.77.99` does not match the intended DNS server for this private lab. A direct lookup against the intended lab DNS server works, so correct the client NIC DNS to `172.28.77.10`. The observed Pro edition already meets the edition gate; an OS purchase would not fix this resolver error. In real troubleshooting, also confirm the displayed observations are current.

Proposed validation: first rerun the SRV lookup without overriding the server and expect the lab DC record. Then, using authorized lab credentials, attempt the join; after a successful join and restart, inspect domain membership and sign in as the synthetic domain user. These are expected checks, not completed results. A responding ping alone would not establish working AD discovery or authentication. If discovery works but the join still fails, collect the new error before proposing another change.

Do not change the router, disable firewall protection, or expose the DC. All changes belong to the disposable, isolated client. Verify scope before touching anything.

Sample note: “LAB-001: domain discovery failed. Client used DNS .99; direct lookup against .10 found the DC. Proposed correction: client DNS to .10 only. Expected validation: normal SRV lookup succeeds, join completes, and a domain sign-in works. No live test performed in this paper exercise.”

## Self-check

You understood the ticket if you chose the resolver evidence, limited the change to the client, separated discovery from authentication, and did not turn an expected result into a completed result. If you chose the router, a public DNS resolver, or firewall shutdown, reread the intended private topology.

## Further reading

Microsoft documents the supported client editions and join prerequisites in [Join a computer to a domain](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/join-computer-to-domain), and explains how AD uses service-location records in [Verify DNS SRV records for a domain controller](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/verify-srv-dns-records-have-been-created).

## Questions or feedback

Tell us which part of the ticket was unclear. Contact [rj@vexonit.com](mailto:rj@vexonit.com) for lesson and partnership inquiries, or [support@vexonit.com](mailto:support@vexonit.com) for a support inquiry. Do not include passwords, account recovery codes, or private customer data.

You may read, print, and complete this free lesson for personal learning. For classroom redistribution or commercial reuse, contact RJ. This exercise does not confer a certification or promise employment.

[Back to Vexon IT selected work](../../README.md)
