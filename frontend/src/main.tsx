import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "@xyflow/react/dist/style.css";
import "./tokens.css";
import "./base.css";
import "./components.css";
import "./product.css";
import App from "./App";
import { AuthProvider } from "./auth/AuthProvider";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
