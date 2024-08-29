// src/layouts/MainLayout.jsx
import { Outlet } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Header from "../components/Common/Header";
import Sidebar from "../components/Common/Sidebar";
import Footer from "../components/Common/Footer";

const MainLayout = () => {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-6 bg-gray-100">
          <Outlet />
        </main>
        <Footer /> {/* Added Footer Component */}
        <ToastContainer />
      </div>
    </div>
  );
};

export default MainLayout;
