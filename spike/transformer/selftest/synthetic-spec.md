# Branch Lending Service — Requirements (synthetic self-test text)

This document is synthetic. It was written for the C1 transformer self-test and describes no real system.

# 1. Members

The service shall register a member with a name and a contact address.
A member may hold at most five loans at any one time.
Membership numbers are assigned as defined in Annex C.

# 2. Loans

The service shall record every checkout and shall send the member a receipt.
Loan records are kept durably and must survive a restart of the service.
For example, a librarian might extend a loan by a week when the member asks at the desk.
Members may borrow up to eight items at a time.

# 3. Notices

Overdue notices are sent to the member and the branch manager or the duty librarian.
The service shall show the catalogue search results promptly.
The service shall not delete a loan record while the loan is open.
