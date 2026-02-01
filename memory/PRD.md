# FinTrack - Personal Finance Dashboard

## Original Problem Statement
Build a visual analytics dashboard website to display income and spending data with:
- Dark/light theme toggle
- Date range filtering
- Data tables with search and export
- Interactive charts (Income vs Spending, Category breakdown)
- Total Income vs Total Spending comparison
- Currency in IQD (Iraqi Dinar)
- MongoDB database for persistent storage and CRUD operations

## Architecture
- **Frontend**: React with Tailwind CSS, Shadcn/UI components, Recharts, Framer Motion
- **Backend**: FastAPI with MongoDB (Motor async driver)
- **Database**: MongoDB with collections for `spendings` and `income`

## User Personas
- Individual user tracking personal finances over time
- Needs to add new spending/income entries regularly
- Wants visual insights into spending patterns

## Core Requirements (Static)
1. Display financial statistics (Total Income, Spending, Net Balance, Savings)
2. Interactive charts for trend analysis
3. Category-wise spending breakdown
4. Data tables with search, sort, and export
5. Dark/Light theme support
6. Date range filtering
7. CRUD operations for spending and income

## What's Been Implemented (Jan 31, 2026)
- [x] Full dashboard with stat cards and charts
- [x] MongoDB backend with full CRUD APIs
- [x] Add Spending dialog with category selection
- [x] Add Income dialog with month picker
- [x] Delete functionality for entries
- [x] Export to CSV functionality
- [x] Dark/Light theme toggle
- [x] Date range filter
- [x] Data seeding functionality
- [x] Responsive design

## API Endpoints
- `GET /api/spendings` - List all spendings
- `POST /api/spendings` - Create spending
- `PUT /api/spendings/{id}` - Update spending
- `DELETE /api/spendings/{id}` - Delete spending
- `GET /api/income` - List all income records
- `POST /api/income` - Create income
- `PUT /api/income/{month}` - Update income
- `DELETE /api/income/{month}` - Delete income
- `GET /api/statistics` - Get summary stats
- `POST /api/seed` - Seed initial data

## Prioritized Backlog
### P0 (Done)
- Dashboard with charts ✓
- CRUD operations ✓
- Theme toggle ✓

### P1 (Future)
- Edit spending/income entries inline
- Budget goals and alerts
- Recurring expense tracking

### P2 (Enhancement)
- Multi-currency support
- Data import from CSV/Excel
- Monthly spending reports via email
