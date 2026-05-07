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
import FacebookImport from "./pages/FacebookImport";
import FortuneA8Offers from "./pages/FortuneA8Offers";
import NoteCtaTemplates from "./pages/NoteCtaTemplates";
import NoteFunnelPages from "./pages/NoteFunnelPages";
import ThirtyDayPlan from "./pages/ThirtyDayPlan";
import ThreadsPostTemplates from "./pages/ThreadsPostTemplates";
import TypefullyJobs from "./pages/TypefullyJobs";
import TypefullySettings from "./pages/TypefullySettings";
import { Page } from "./types";

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [reloadKey, setReloadKey] = useState(0);

  return (
    <Layout page={page} onPageChange={setPage} onRefresh={() => setReloadKey((value) => value + 1)}>
      <div key={`${page}-${reloadKey}`}>
        {page === "dashboard" && <Dashboard />}
        {page === "thirty-day-plan" && <ThirtyDayPlan />}
        {page === "typefully-jobs" && <TypefullyJobs />}
        {page === "knowledge" && <Knowledge />}
        {page === "facebook-import" && <FacebookImport />}
        {page === "products" && <AffiliateProducts />}
        {page === "note-funnel" && <NoteFunnelPages />}
        {page === "fortune-a8-offers" && <FortuneA8Offers />}
        {page === "note-ctas" && <NoteCtaTemplates />}
        {page === "persona-pains" && <PersonaPains />}
        {page === "fortune-templates" && <FortuneTemplates />}
        {page === "threads-templates" && <ThreadsPostTemplates />}
        {page === "generator" && <ContentGenerator />}
        {page === "drafts" && <Drafts />}
        {page === "typefully-settings" && <TypefullySettings />}
        {page === "settings" && <Settings />}
      </div>
    </Layout>
  );
}
