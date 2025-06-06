import { useLocation } from "react-router-dom";
import { CompositeProvider } from "./module/composite-stream/provider/CompositeProvider";
import { MainView } from "./module/composite-stream/components/MainView";

export const RoutedApp = () => {
  const location = useLocation();
  const language = location.pathname.replace("/", "")

  return (
    <CompositeProvider language={language}>
      <MainView />
    </CompositeProvider>
  );
};
