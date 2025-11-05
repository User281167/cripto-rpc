import { Route, Routes } from "react-router-dom";

import IndexPage from "@/pages/index";
import CryptoPage from "@/pages/crypto";

function App() {
  return (
    <Routes>
      <Route element={<IndexPage />} path="/" />
      <Route element={<CryptoPage />} path="/:id" />
    </Routes>
  );
}

export default App;
