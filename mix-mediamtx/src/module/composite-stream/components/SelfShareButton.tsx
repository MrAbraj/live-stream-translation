import { Button } from "@chakra-ui/react";
import { useCompositeContext } from "../provider/CompositeProvider";

export const SelfShareButton = () => {
  const { startSharingTab } = useCompositeContext();

  const hideButtonStyle = {
    color: "transparent",
    backgroundColor: "transparent",
    border: "none",
  };
  return (
    <Button
      onClick={startSharingTab}
      style={{ ...hideButtonStyle }}
      position="fixed"
      bottom={0}
      right={0}
      color="red"
      id="self_share_btn"
    >
      Share Self
    </Button>
  );
};
