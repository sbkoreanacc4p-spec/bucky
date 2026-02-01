import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ========== Spendings API ==========

export const fetchSpendings = async () => {
  const response = await axios.get(`${API}/spendings`);
  return response.data;
};

export const createSpending = async (spending) => {
  const response = await axios.post(`${API}/spendings`, spending);
  return response.data;
};

export const updateSpending = async (id, spending) => {
  const response = await axios.put(`${API}/spendings/${id}`, spending);
  return response.data;
};

export const deleteSpending = async (id) => {
  const response = await axios.delete(`${API}/spendings/${id}`);
  return response.data;
};

// ========== Income API ==========

export const fetchIncome = async () => {
  const response = await axios.get(`${API}/income`);
  return response.data;
};

export const createIncome = async (income) => {
  const response = await axios.post(`${API}/income`, income);
  return response.data;
};

export const updateIncome = async (month, income) => {
  const response = await axios.put(`${API}/income/${month}`, income);
  return response.data;
};

export const deleteIncome = async (month) => {
  const response = await axios.delete(`${API}/income/${month}`);
  return response.data;
};

// ========== Statistics API ==========

export const fetchStatistics = async () => {
  const response = await axios.get(`${API}/statistics`);
  return response.data;
};

// ========== Seed Data ==========

export const seedData = async () => {
  const response = await axios.post(`${API}/seed`);
  return response.data;
};
