// Helper function to format currency
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IQ', {
    style: 'decimal',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount) + ' IQD';
};

// Helper function to format compact currency
export const formatCompactCurrency = (amount) => {
  if (amount >= 1000000) {
    return (amount / 1000000).toFixed(1) + 'M IQD';
  } else if (amount >= 1000) {
    return (amount / 1000).toFixed(0) + 'K IQD';
  }
  return amount + ' IQD';
};

// Get month name from date string
export const getMonthName = (dateStr) => {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const [year, month] = dateStr.split('-');
  return `${months[parseInt(month) - 1]} ${year.slice(2)}`;
};

// Get spending by category
export const getSpendingByCategory = (spendings) => {
  const categoryMap = {};
  spendings.forEach(item => {
    // Normalize category names
    let category = item.category;
    if (category === 'College-Project') category = 'College Project';
    if (category === 'Care Care') category = 'Car Care';
    
    if (categoryMap[category]) {
      categoryMap[category] += item.amount;
    } else {
      categoryMap[category] = item.amount;
    }
  });
  
  return Object.entries(categoryMap)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
};

// Get monthly comparison data
export const getMonthlyComparison = (spendings, income) => {
  const monthlySpending = {};
  
  spendings.forEach(item => {
    const month = item.date.substring(0, 7);
    if (monthlySpending[month]) {
      monthlySpending[month] += item.amount;
    } else {
      monthlySpending[month] = item.amount;
    }
  });
  
  return income.map(item => ({
    month: getMonthName(item.month),
    fullMonth: item.month,
    income: item.income,
    spending: monthlySpending[item.month] || 0,
    saved: item.saved || 0,
    net: item.income - (monthlySpending[item.month] || 0)
  })).sort((a, b) => a.fullMonth.localeCompare(b.fullMonth));
};

// Filter spendings by date range
export const filterByDateRange = (data, startDate, endDate) => {
  if (!startDate && !endDate) return data;
  
  return data.filter(item => {
    const itemDate = new Date(item.date);
    if (startDate && itemDate < startDate) return false;
    if (endDate && itemDate > endDate) return false;
    return true;
  });
};

// Filter income by date range
export const filterIncomeByDateRange = (data, startDate, endDate) => {
  if (!startDate && !endDate) return data;
  
  return data.filter(item => {
    const [year, month] = item.month.split('-');
    const itemDate = new Date(parseInt(year), parseInt(month) - 1, 1);
    if (startDate && itemDate < new Date(startDate.getFullYear(), startDate.getMonth(), 1)) return false;
    if (endDate && itemDate > new Date(endDate.getFullYear(), endDate.getMonth(), 1)) return false;
    return true;
  });
};
