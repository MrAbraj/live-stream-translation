import { Box, Flex, Grid, GridItem, Spacer, Stack } from "@chakra-ui/react";
import { useCompositeContext } from "../provider/CompositeProvider";
import { VideoPlayer } from "./VideoPlayer";

export const DisplayGridView = () => {
  const { webCamStreams, displayStreams } = useCompositeContext();
  const displayStream = Array.from(displayStreams.values()).filter(
    (stream): stream is MediaStream => stream !== undefined
  );
  const streams = Array.from(webCamStreams.values()).filter(
    (stream): stream is MediaStream => stream !== undefined
  );
  const totalStreams = streams.length;
  const columns = Math.ceil(totalStreams / 6);

  return (
    <Flex mt={2} height="100vh" width="100vw" id="display-grid-view-container">
      <Box width="18%" height="100%" id="display-grid-view" pr={1} mx={3} pt="10%">
        <Grid
          templateColumns={`repeat(${columns}, 1fr)`}
          templateRows={`repeat(4, 1fr)`}
          gap={2}
          height="100%"
          top="50%"
        >
          {streams.map((stream, index) => (
            <GridItem key={index}>
              <VideoPlayer stream={stream} />
            </GridItem>
          ))}
          {streams.map((stream, index) => (
            <GridItem key={index}>
              <VideoPlayer stream={stream} />
            </GridItem>
          ))}
        </Grid>
      </Box>
      <Box width="85%" height="100%" mr={1}>
        <VideoPlayer stream={displayStream[0]} />
      </Box>
    </Flex>
  );
};
