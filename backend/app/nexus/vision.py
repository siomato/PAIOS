class VisionInput:

    def process(self, frame):

        return {
            "source": "vision",
            "data": frame
        }


vision = VisionInput()