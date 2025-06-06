import { Flex } from "@chakra-ui/react";
import { DisplayGridView } from "./DisplayGridView";
import { WebCamGridView } from "./WebCamGridView";
import { useCompositeContext } from "../provider/CompositeProvider";
import { SelfShareButton } from "./SelfShareButton";

export const MainView = () => {
  const { webCamStreams, displayStreams } = useCompositeContext();
  const displayStream = Array.from(displayStreams.values()).filter(
    (stream): stream is MediaStream => stream !== undefined
  );
  console.log("displayStream", displayStream);
  const webCamStream = Array.from(webCamStreams.values()).filter(
    (stream): stream is MediaStream => stream !== undefined
  );
  const isDisplayStreamAvailable = displayStream.length > 0;
  const isWebCamStreamAvailable = webCamStream.length > 0;

  if (!isDisplayStreamAvailable && !isWebCamStreamAvailable) {
    return (
      <Flex
        height="100vh"
        width="100vw"
        justifyContent="center"
        alignItems="center"
        color="red"
      >
        No streams available
      </Flex>
    );
  }
  return (
    <Flex
      height="100vh"
      width="100vw"
      boxSizing="border-box"
      alignContent="center"
      justifyContent="center"
      overflow="hidden"
      id="main-view"
      bgColor="black"
      // mt={2}
    >
      {isDisplayStreamAvailable ? <DisplayGridView /> : <WebCamGridView />}
      <SelfShareButton />
    </Flex>
  );
};
