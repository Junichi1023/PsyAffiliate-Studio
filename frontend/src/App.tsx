import { useState } from "react";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Knowledge from "./pages/Knowledge";
import AffiliateProducts from "./pages/AffiliateProducts";
import PersonaPains from "./pages/PersonaPains";
import FortuneTemplates from "./pages/FortuneTemplates";
import ContentGenerator from "./pages/ContentGenerator";
import Drafts from "./pages/Drafts";
import Settings from "./pages/Settings";
import { Page } from "./types";

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [reloadKey, setReloadKey] = useState(0);

  return (
    <Layout page={page} onPageChange={setPage} onRefresh={() => setReloadKey((value) => value + 1)}>
      <div key={`${page}-${reloadKey}`}>
        {page === "dashboard" && <Dashboard />}
        {page === "knowledge" && <Knowledge />}
        {page === "products" && <AffiliateProducts />}
        {page === "persona-pains" && <PersonaPains />}
        {page === "fortune-templates" && <FortuneTemplates />}
        {page === "generator" && <ContentGenerator />}
        {page === "drafts" && <Drafts />}
        {page === "settings" && <Settings />}
      </div>
    </Layout>
  );
}
