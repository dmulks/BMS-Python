
# Frontend Setup (React)

## Prerequisites

- Node.js 18+
- npm or yarn
- Backend running at `http://localhost:8000`

---

## Steps

### 1. Create React App (Vite Example)

```bash
npm create vite@latest bond-frontend --template react
cd bond-frontend
npm install
```

### 2. Install Dependencies

```bash
npm install axios react-router-dom
```

### 3. Project Structure

```text
src/
  api/
    client.js
  layout/
    AppLayout.jsx
  pages/
    Dashboard.jsx
    BondList.jsx
    BondDetail.jsx
    BondPaymentPreview.jsx
    MemberList.jsx
    MemberDetail.jsx
    MemberPaymentsReport.jsx
    AdminAuditReport.jsx
    BozStatementUpload.jsx
  main.jsx
```

### 4. Axios Client

`src/api/client.js`:

```js
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

export default api;
```

### 5. Layout & Router

Configure `AppLayout` and routes in `main.jsx` or `index.jsx` to match:

- `/` → Dashboard
- `/bonds` → BondList
- `/bonds/:bondId` → BondDetail
- `/bonds/:bondId/events/:eventId/preview` → BondPaymentPreview
- `/members` → MemberList
- `/members/:memberId` → MemberDetail
- `/members/:memberId/payments` → MemberPaymentsReport
- `/admin/audit` → AdminAuditReport
- `/admin/boz-upload` → BozStatementUpload

### 6. Run Frontend

```bash
npm run dev
# or
npm start
```

Visit the app at the dev URL (e.g. `http://localhost:5173`) and confirm:

- Dashboard loads from `GET /dashboard`.
- Preview page loads from `GET /bonds/{bondId}/payments/preview?event_id=...`.
