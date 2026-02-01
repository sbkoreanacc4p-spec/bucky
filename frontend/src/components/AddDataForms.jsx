import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, X, Save, Calendar, DollarSign, Tag } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { toast } from 'sonner';
import { createSpending, createIncome } from '../lib/api';

const COMMON_CATEGORIES = [
  'Food', 'Taxi', 'Fuel', 'Internet', 'Gaming', 'Barber',
  'Car Care', 'Car Wash', 'Parking', 'Korek', 'Shopping',
  'Healthcare', 'Education', 'Entertainment', 'Other'
];

export const AddSpendingDialog = ({ onSuccess }) => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    category: '',
    customCategory: '',
    date: new Date().toISOString().split('T')[0],
    amount: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const category = form.category === 'Other' ? form.customCategory : form.category;
    
    if (!category || !form.date || !form.amount) {
      toast.error('Please fill all required fields');
      return;
    }

    setLoading(true);
    try {
      await createSpending({
        category,
        date: form.date,
        amount: parseFloat(form.amount)
      });
      toast.success('Spending added successfully!');
      setOpen(false);
      setForm({ category: '', customCategory: '', date: new Date().toISOString().split('T')[0], amount: '' });
      onSuccess?.();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add spending');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button 
          className="bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white"
          data-testid="add-spending-btn"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Spending
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-red-500" />
            Add New Spending
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Category</Label>
            <Select 
              value={form.category} 
              onValueChange={(value) => setForm({ ...form, category: value })}
            >
              <SelectTrigger data-testid="spending-category-select">
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                {COMMON_CATEGORIES.map((cat) => (
                  <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <AnimatePresence>
            {form.category === 'Other' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-2"
              >
                <Label>Custom Category</Label>
                <Input
                  placeholder="Enter category name"
                  value={form.customCategory}
                  onChange={(e) => setForm({ ...form, customCategory: e.target.value })}
                  data-testid="spending-custom-category"
                />
              </motion.div>
            )}
          </AnimatePresence>
          
          <div className="space-y-2">
            <Label>Date</Label>
            <Input
              type="date"
              value={form.date}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
              data-testid="spending-date"
            />
          </div>
          
          <div className="space-y-2">
            <Label>Amount (IQD)</Label>
            <Input
              type="number"
              placeholder="0"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              data-testid="spending-amount"
            />
          </div>
          
          <div className="flex gap-3 pt-4">
            <Button 
              type="button" 
              variant="outline" 
              className="flex-1"
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              className="flex-1 bg-red-500 hover:bg-red-600"
              disabled={loading}
              data-testid="save-spending-btn"
            >
              {loading ? 'Saving...' : 'Save Spending'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export const AddIncomeDialog = ({ onSuccess }) => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    month: new Date().toISOString().slice(0, 7),
    income: '',
    saved: '0',
    home: '0'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!form.month || !form.income) {
      toast.error('Please fill month and income fields');
      return;
    }

    setLoading(true);
    try {
      await createIncome({
        month: form.month,
        income: parseFloat(form.income),
        saved: parseFloat(form.saved) || 0,
        home: parseFloat(form.home) || 0
      });
      toast.success('Income added successfully!');
      setOpen(false);
      setForm({ month: new Date().toISOString().slice(0, 7), income: '', saved: '0', home: '0' });
      onSuccess?.();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add income');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button 
          className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white"
          data-testid="add-income-btn"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Income
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-emerald-500" />
            Add Monthly Income
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Month</Label>
            <Input
              type="month"
              value={form.month}
              onChange={(e) => setForm({ ...form, month: e.target.value })}
              data-testid="income-month"
            />
          </div>
          
          <div className="space-y-2">
            <Label>Income (IQD)</Label>
            <Input
              type="number"
              placeholder="0"
              value={form.income}
              onChange={(e) => setForm({ ...form, income: e.target.value })}
              data-testid="income-amount"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Saved (IQD)</Label>
              <Input
                type="number"
                placeholder="0"
                value={form.saved}
                onChange={(e) => setForm({ ...form, saved: e.target.value })}
                data-testid="income-saved"
              />
            </div>
            
            <div className="space-y-2">
              <Label>Home (IQD)</Label>
              <Input
                type="number"
                placeholder="0"
                value={form.home}
                onChange={(e) => setForm({ ...form, home: e.target.value })}
                data-testid="income-home"
              />
            </div>
          </div>
          
          <div className="flex gap-3 pt-4">
            <Button 
              type="button" 
              variant="outline" 
              className="flex-1"
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              className="flex-1 bg-emerald-500 hover:bg-emerald-600"
              disabled={loading}
              data-testid="save-income-btn"
            >
              {loading ? 'Saving...' : 'Save Income'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};
