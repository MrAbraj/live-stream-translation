import { defaultSystem } from "@chakra-ui/react"
import { ChakraProvider } from "@chakra-ui/react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { RoutedApp } from "./RoutedApp";

function App() {
  return (
    <ChakraProvider value={defaultSystem}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RoutedApp />} />
          <Route path="/hindi" element={<RoutedApp />} />
        </Routes>
      </BrowserRouter>
    </ChakraProvider>
  );
}

export default App;
