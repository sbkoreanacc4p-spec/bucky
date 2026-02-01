import { useState, useEffect, useMemo, useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  Wallet, 
  PiggyBank, 
  LayoutDashboard,
  Table as TableIcon,
  RefreshCw,
  Database
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
import { AddSpendingDialog, AddIncomeDialog } from './components/AddDataForms';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Button } from './components/ui/button';
import { Toaster, toast } from './components/ui/sonner';

import { fetchSpendings, fetchIncome, seedData } from './lib/api';
import {
  formatCurrency,
  getSpendingByCategory,
  getMonthlyComparison,
  filterByDateRange,
  filterIncomeByDateRange
} from './lib/data';

import '@/App.css';

const Dashboard = () => {
  const [dateRange, setDateRange] = useState({ from: null, to: null });
  const [activeTab, setActiveTab] = useState('dashboard');
  const [spendings, setSpendings] = useState([]);
  const [income, setIncome] = useState([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);

  // Fetch data from API
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [spendingsData, incomeData] = await Promise.all([
        fetchSpendings(),
        fetchIncome()
      ]);
      setSpendings(spendingsData);
      setIncome(incomeData);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Seed initial data
  const handleSeedData = async () => {
    setSeeding(true);
    try {
      const result = await seedData();
      toast.success(result.message);
      await loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to seed data');
    } finally {
      setSeeding(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Filter data based on date range
  const filteredSpendings = useMemo(() => {
    return filterByDateRange(spendings, dateRange.from, dateRange.to);
  }, [spendings, dateRange]);

  const filteredIncome = useMemo(() => {
    return filterIncomeByDateRange(income, dateRange.from, dateRange.to);
  }, [income, dateRange]);

  // Calculate statistics
  const totals = useMemo(() => {
    const totalSpending = filteredSpendings.reduce((sum, item) => sum + item.amount, 0);
    const totalIncome = filteredIncome.reduce((sum, item) => sum + item.income, 0);
    const totalSaved = filteredIncome.reduce((sum, item) => sum + (item.saved || 0), 0);
    const totalHome = filteredIncome.reduce((sum, item) => sum + (item.home || 0), 0);
    const netBalance = totalIncome - totalSpending;
    
    return { totalSpending, totalIncome, totalSaved, totalHome, netBalance };
  }, [filteredSpendings, filteredIncome]);

  const categoryData = useMemo(() => {
    return getSpendingByCategory(filteredSpendings);
  }, [filteredSpendings]);

  const monthlyComparison = useMemo(() => {
    return getMonthlyComparison(filteredSpendings, filteredIncome);
  }, [filteredSpendings, filteredIncome]);

  // Show empty state if no data
  const hasNoData = !loading && spendings.length === 0 && income.length === 0;

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
          <div className="flex flex-wrap items-center gap-3">
            <DateRangeFilter 
              dateRange={dateRange} 
              onDateRangeChange={setDateRange} 
            />
            <Button 
              variant="outline" 
              size="icon"
              onClick={loadData}
              disabled={loading}
              data-testid="refresh-data-btn"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>

        {/* Empty State */}
        {hasNoData ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center py-20 text-center"
          >
            <div className="p-4 rounded-full bg-muted mb-4">
              <Database className="w-12 h-12 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No Data Yet</h3>
            <p className="text-muted-foreground mb-6 max-w-md">
              Your database is empty. Click the button below to load your initial spending and income data, or start adding entries manually.
            </p>
            <div className="flex flex-wrap gap-3 justify-center">
              <Button 
                onClick={handleSeedData}
                disabled={seeding}
                className="bg-gradient-to-r from-blue-600 to-violet-600"
                data-testid="seed-data-btn"
              >
                {seeding ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Loading Data...
                  </>
                ) : (
                  <>
                    <Database className="w-4 h-4 mr-2" />
                    Load Initial Data
                  </>
                )}
              </Button>
              <AddSpendingDialog onSuccess={loadData} />
              <AddIncomeDialog onSuccess={loadData} />
            </div>
          </motion.div>
        ) : (
          <>
            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3 mb-6">
              <AddSpendingDialog onSuccess={loadData} />
              <AddIncomeDialog onSuccess={loadData} />
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
                  <SpendingsTable data={filteredSpendings} onRefresh={loadData} />
                  <IncomeTable data={filteredIncome} onRefresh={loadData} />
                </div>
              </TabsContent>
            </Tabs>
          </>
        )}

        {/* Footer */}
        <motion.footer 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-12 pt-8 border-t border-border/50 text-center text-sm text-muted-foreground"
        >
          <p>Data range: March 2025 - Present</p>
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
