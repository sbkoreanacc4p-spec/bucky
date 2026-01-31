import { useState, useMemo } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  Wallet, 
  PiggyBank, 
  ArrowUpDown,
  LayoutDashboard,
  Table as TableIcon
} from 'lucide-react';

import { ThemeProvider } from './context/ThemeContext';
import { Header } from './components/Header';
import { StatCard } from './components/StatCard';
import { DateRangeFilter } from './components/DateRangeFilter';
import { 
  IncomeVsSpendingChart, 
  CategoryPieChart, 
  TopCategoriesChart,
  MonthlyNetChart
} from './components/Charts';
import { SpendingsTable, IncomeTable } from './components/DataTable';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Toaster } from './components/ui/sonner';

import {
  spendingsData,
  incomeData,
  calculateTotals,
  getSpendingByCategory,
  getMonthlyComparison,
  filterByDateRange,
  filterIncomeByDateRange
} from './lib/data';

import '@/App.css';

const Dashboard = () => {
  const [dateRange, setDateRange] = useState({ from: null, to: null });
  const [activeTab, setActiveTab] = useState('dashboard');

  // Filter data based on date range
  const filteredSpendings = useMemo(() => {
    return filterByDateRange(spendingsData, dateRange.from, dateRange.to);
  }, [dateRange]);

  const filteredIncome = useMemo(() => {
    return filterIncomeByDateRange(incomeData, dateRange.from, dateRange.to);
  }, [dateRange]);

  // Calculate statistics
  const totals = useMemo(() => {
    return calculateTotals(filteredSpendings, filteredIncome);
  }, [filteredSpendings, filteredIncome]);

  const categoryData = useMemo(() => {
    return getSpendingByCategory(filteredSpendings);
  }, [filteredSpendings]);

  const monthlyComparison = useMemo(() => {
    return getMonthlyComparison(filteredSpendings, filteredIncome);
  }, [filteredSpendings, filteredIncome]);

  return (
    <div className="min-h-screen bg-background" data-testid="dashboard-container">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Title and Filter Section */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <motion.h2 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-2xl sm:text-3xl font-bold tracking-tight"
            >
              Financial Overview
            </motion.h2>
            <motion.p 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="text-muted-foreground mt-1"
            >
              Track your income, spending, and savings
            </motion.p>
          </div>
          <DateRangeFilter 
            dateRange={dateRange} 
            onDateRangeChange={setDateRange} 
          />
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="Total Income"
            value={totals.totalIncome}
            icon={TrendingUp}
            variant="income"
            delay={0}
          />
          <StatCard
            title="Total Spending"
            value={totals.totalSpending}
            icon={TrendingDown}
            variant="spending"
            delay={0.1}
          />
          <StatCard
            title="Net Balance"
            value={totals.netBalance}
            icon={Wallet}
            variant="balance"
            trend={totals.netBalance >= 0 ? 'up' : 'down'}
            trendValue={totals.netBalance >= 0 ? 'Positive' : 'Negative'}
            delay={0.2}
          />
          <StatCard
            title="Total Saved"
            value={totals.totalSaved}
            icon={PiggyBank}
            variant="savings"
            delay={0.3}
          />
        </div>

        {/* Tabs for Dashboard and Tables */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="dashboard" data-testid="dashboard-tab">
              <LayoutDashboard className="w-4 h-4 mr-2" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="tables" data-testid="tables-tab">
              <TableIcon className="w-4 h-4 mr-2" />
              Data Tables
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-6">
            {/* Main Chart */}
            <IncomeVsSpendingChart data={monthlyComparison} />
            
            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CategoryPieChart data={categoryData} total={totals.totalSpending} />
              <TopCategoriesChart data={categoryData} />
            </div>
            
            {/* Net Balance Chart */}
            <MonthlyNetChart data={monthlyComparison} />
          </TabsContent>

          <TabsContent value="tables" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SpendingsTable data={filteredSpendings} />
              <IncomeTable data={filteredIncome} />
            </div>
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <motion.footer 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-12 pt-8 border-t border-border/50 text-center text-sm text-muted-foreground"
        >
          <p>Data range: March 2025 - January 2026</p>
          <p className="mt-1">Built with care for personal finance tracking</p>
        </motion.footer>
      </main>
      
      <Toaster position="top-right" />
    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
