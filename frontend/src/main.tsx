import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import "./styles.css";
import WorkbenchPage from "./pages/WorkbenchPage";
import ArchitecturePage from "./pages/ArchitecturePage";

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element #root not found");
}

createRoot(rootElement).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<WorkbenchPage />} />
        <Route path="/architecture" element={<ArchitecturePage />} />
        <Route path="*" element={<WorkbenchPage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
);
