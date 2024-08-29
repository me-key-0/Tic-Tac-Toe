import { Outlet } from "react-router-dom";
import Header from "../components/Common/Header";
import Sidebar from "../components/Common/Sidebar";
import Footer from "../components/Common/Footer";

const MainLayout = () => {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-6 bg-gray-100 overflow-y-auto">
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  );
};

export default MainLayout;
