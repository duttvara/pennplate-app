import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import App from "./App";
import Home from "./pages/Home";
import Results from "./pages/Results";
import DiningHall from "./pages/DiningHall";
import "./styles.css";
import { AuthProvider } from "./auth/AuthContext";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider><BrowserRouter>
      <Routes><Route element={<App />}><Route path="/" element={<Home />} /><Route path="/results" element={<Results />} /><Route path="/hall/:hallSlug" element={<DiningHall />} /></Route></Routes>
    </BrowserRouter></AuthProvider>
  </React.StrictMode>
);
