import { Flex, Grid, GridItem } from "@chakra-ui/react";
import { useCompositeContext } from "../provider/CompositeProvider";
import { VideoPlayer } from "./VideoPlayer";

export const WebCamGridView = () => {
  const { webCamStreams } = useCompositeContext();
  const streams = Array.from(webCamStreams.values()).filter(
    (stream): stream is MediaStream => stream !== undefined
  );
  const totalStreams = streams.length;
  const columns = Math.ceil(Math.sqrt(totalStreams));
  const rows = Math.ceil(totalStreams / columns);
  return (
    <Flex
      width="100%"
      height="100%"
      alignItems="center"
      justifyContent="center"
      id="webcam-grid-view"
    >
      <Grid
        templateColumns={`repeat(${columns}, 1fr)`}
        templateRows={`repeat(${rows}, 1fr)`}
        gap={4}
        width="auto"
        height="auto"
      >
        {streams.map((stream, index) => (
          <GridItem key={index}>
            <VideoPlayer stream={stream} />
          </GridItem>
        ))}
      </Grid>
    </Flex>
  );
};
