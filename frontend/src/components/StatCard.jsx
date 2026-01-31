import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { formatCurrency } from '../lib/data';

export const StatCard = ({ 
  title, 
  value, 
  icon: Icon, 
  trend, 
  trendValue, 
  className = '',
  delay = 0,
  variant = 'default'
}) => {
  const getTrendIcon = () => {
    if (!trend) return null;
    if (trend === 'up') return <TrendingUp className="w-4 h-4" />;
    if (trend === 'down') return <TrendingDown className="w-4 h-4" />;
    return <Minus className="w-4 h-4" />;
  };

  const getTrendColor = () => {
    if (variant === 'spending') {
      return trend === 'up' ? 'text-red-400' : 'text-emerald-400';
    }
    if (trend === 'up') return 'text-emerald-400';
    if (trend === 'down') return 'text-red-400';
    return 'text-muted-foreground';
  };

  const getVariantStyles = () => {
    switch (variant) {
      case 'income':
        return 'border-emerald-500/20 bg-emerald-500/5';
      case 'spending':
        return 'border-red-500/20 bg-red-500/5';
      case 'savings':
        return 'border-blue-500/20 bg-blue-500/5';
      case 'balance':
        return 'border-violet-500/20 bg-violet-500/5';
      default:
        return 'border-border/50 bg-card/50';
    }
  };

  const getIconBgColor = () => {
    switch (variant) {
      case 'income':
        return 'bg-emerald-500/10 text-emerald-500';
      case 'spending':
        return 'bg-red-500/10 text-red-500';
      case 'savings':
        return 'bg-blue-500/10 text-blue-500';
      case 'balance':
        return 'bg-violet-500/10 text-violet-500';
      default:
        return 'bg-primary/10 text-primary';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className={`relative overflow-hidden rounded-xl border backdrop-blur-xl p-6 ${getVariantStyles()} ${className}`}
      data-testid={`stat-card-${variant}`}
    >
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 rounded-lg ${getIconBgColor()}`}>
            {Icon && <Icon className="w-5 h-5" />}
          </div>
          {trend && (
            <div className={`flex items-center gap-1 text-sm font-medium ${getTrendColor()}`}>
              {getTrendIcon()}
              <span>{trendValue}</span>
            </div>
          )}
        </div>
        
        <div>
          <p className="text-sm font-medium text-muted-foreground mb-1">{title}</p>
          <p className="text-2xl font-bold tracking-tight font-mono">
            {typeof value === 'number' ? formatCurrency(value) : value}
          </p>
        </div>
      </div>
    </motion.div>
  );
};
