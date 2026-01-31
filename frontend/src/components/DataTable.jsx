import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { ChevronUp, ChevronDown, Search, Download } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';
import { ScrollArea } from './ui/scroll-area';
import { formatCurrency, getMonthName } from '../lib/data';

export const SpendingsTable = ({ data, onExport }) => {
  const [sortField, setSortField] = useState('date');
  const [sortDirection, setSortDirection] = useState('desc');
  const [searchTerm, setSearchTerm] = useState('');

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const filteredAndSortedData = useMemo(() => {
    let filtered = data;
    
    if (searchTerm) {
      filtered = data.filter(item => 
        item.category.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    return [...filtered].sort((a, b) => {
      let comparison = 0;
      if (sortField === 'date') {
        comparison = new Date(a.date) - new Date(b.date);
      } else if (sortField === 'amount') {
        comparison = a.amount - b.amount;
      } else if (sortField === 'category') {
        comparison = a.category.localeCompare(b.category);
      }
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [data, sortField, sortDirection, searchTerm]);

  const SortIcon = ({ field }) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? 
      <ChevronUp className="w-4 h-4 inline ml-1" /> : 
      <ChevronDown className="w-4 h-4 inline ml-1" />;
  };

  const exportToCSV = () => {
    const headers = ['Category', 'Date', 'Amount (IQD)'];
    const rows = filteredAndSortedData.map(item => [
      item.category,
      item.date,
      item.amount
    ]);
    
    const csvContent = [headers, ...rows]
      .map(row => row.join(','))
      .join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'spendings_export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.5 }}
      className="rounded-xl border border-border/50 bg-card/50 backdrop-blur-xl p-6"
      data-testid="spendings-table"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <h3 className="text-lg font-semibold">Spendings Detail</h3>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search category..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 w-48"
              data-testid="spendings-search"
            />
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={exportToCSV}
            data-testid="export-spendings-btn"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>
      
      <ScrollArea className="h-[400px] rounded-lg border border-border/50">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead 
                className="cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort('category')}
              >
                Category <SortIcon field="category" />
              </TableHead>
              <TableHead 
                className="cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort('date')}
              >
                Date <SortIcon field="date" />
              </TableHead>
              <TableHead 
                className="text-right cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort('amount')}
              >
                Amount <SortIcon field="amount" />
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredAndSortedData.map((item, index) => (
              <TableRow key={`${item.date}-${item.category}-${index}`}>
                <TableCell className="font-medium">{item.category}</TableCell>
                <TableCell className="text-muted-foreground">
                  {new Date(item.date).toLocaleDateString('en-GB', {
                    day: '2-digit',
                    month: 'short',
                    year: 'numeric'
                  })}
                </TableCell>
                <TableCell className="text-right font-mono">
                  {formatCurrency(item.amount)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </ScrollArea>
      
      <div className="mt-4 text-sm text-muted-foreground">
        Showing {filteredAndSortedData.length} of {data.length} transactions
      </div>
    </motion.div>
  );
};

export const IncomeTable = ({ data, onExport }) => {
  const exportToCSV = () => {
    const headers = ['Month', 'Income (IQD)', 'Saved (IQD)', 'Home (IQD)'];
    const rows = data.map(item => [
      item.month,
      item.income,
      item.saved,
      item.home
    ]);
    
    const csvContent = [headers, ...rows]
      .map(row => row.join(','))
      .join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'income_export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.6 }}
      className="rounded-xl border border-border/50 bg-card/50 backdrop-blur-xl p-6"
      data-testid="income-table"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Monthly Income</h3>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={exportToCSV}
          data-testid="export-income-btn"
        >
          <Download className="w-4 h-4 mr-2" />
          Export
        </Button>
      </div>
      
      <ScrollArea className="h-[400px] rounded-lg border border-border/50">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead>Month</TableHead>
              <TableHead className="text-right">Income</TableHead>
              <TableHead className="text-right">Saved</TableHead>
              <TableHead className="text-right">Home</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((item) => (
              <TableRow key={item.month}>
                <TableCell className="font-medium">
                  {getMonthName(item.month)}
                </TableCell>
                <TableCell className="text-right font-mono text-emerald-500">
                  {formatCurrency(item.income)}
                </TableCell>
                <TableCell className="text-right font-mono text-blue-500">
                  {item.saved > 0 ? formatCurrency(item.saved) : '-'}
                </TableCell>
                <TableCell className="text-right font-mono text-amber-500">
                  {item.home > 0 ? formatCurrency(item.home) : '-'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </ScrollArea>
    </motion.div>
  );
};
