
# Frontend Architecture (React)

## Routing Map

```text
/                             → Dashboard
/bonds                        → BondList
/bonds/:bondId                → BondDetail
/bonds/:bondId/events/:eventId/preview
                              → BondPaymentPreview
/members                      → MemberList
/members/:memberId            → MemberDetail
/members/:memberId/payments   → MemberPaymentsReport
/admin/audit                  → AdminAuditReport
/admin/boz-upload             → BozStatementUpload
```

## Layout

### `AppLayout.jsx`

- Sidebar navigation:
  - Dashboard
  - Bonds
  - Members
  - Admin → Audit Report, BOZ CSV Upload
- `<Outlet />` for routed content.

## API Client

`src/api/client.js`:

```js
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

export default api;
```

## Key Pages

### `Dashboard.jsx`

- Calls `GET /dashboard`.
- Shows KPIs and upcoming payment events.

### `BondPaymentPreview.jsx`

- Calls `GET /bonds/:bondId/payments/preview?event_id=...`.
- Shows detailed computed fields per member.
- Actions:
  - `POST /bonds/:bondId/payments/generate`
  - `POST /bonds/:bondId/payments/recalculate`
  - Export preview as CSV.

### `MemberPaymentsReport.jsx`

- Calls `GET /members/:memberId/payments`.
- Shows all payments for one member with totals.

### `AdminAuditReport.jsx`

- Calls `GET /admin/audit`.
- Compares totals vs expected BOZ amounts and highlights differences.

### `BozStatementUpload.jsx`

- Uploads CSV to `/admin/boz-statement-upload`.
- Displays rows processed and events updated.
