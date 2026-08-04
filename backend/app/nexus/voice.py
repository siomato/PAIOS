class VoiceInput:

    def process(self, audio):

        return {
            "source": "voice",
            "data": audio
        }


voice = VoiceInput()