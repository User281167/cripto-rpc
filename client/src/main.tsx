import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App.tsx";
import { Provider } from "./provider.tsx";
import "@/styles/globals.css";

import { SocketProvider } from "@/context/SocketContext.tsx";
import { ExchangeProvider } from "@/context/ExchangeContext.tsx";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Provider>
        <ExchangeProvider>
          <SocketProvider>
            <App />
          </SocketProvider>
        </ExchangeProvider>
      </Provider>
    </BrowserRouter>
  </React.StrictMode>
);
