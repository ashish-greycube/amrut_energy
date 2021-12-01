function get_url_param(url, param) {
    var urlParams = new URLSearchParams(new URL(url).search);
    return urlParams.get(param);
}


frappe.ready(function () {
    start_meeting(
        window.location.href,
    );
});


const start_meeting = function (meeting_url, participant_name = "",) {
    const meeting = new VideoSDKMeeting();

    let meeting_id = get_url_param(meeting_url, 'meeting_id'),
        meeting_title = get_url_param(meeting_url, 'meeting_title'),
        api_key = get_url_param(meeting_url, 'api_key');

    const config = {
        name: participant_name,
        apiKey: api_key,
        meetingId: meeting_id, // enter your meeting id

        containerId: null,
        redirectOnLeave: "https://www.videosdk.live/",

        micEnabled: true,
        webcamEnabled: true,
        participantCanToggleSelfWebcam: true,
        participantCanToggleSelfMic: true,
        maxResolution: "sd", // optional, default: "hd"

        chatEnabled: true,
        screenShareEnabled: true,
        pollEnabled: true,
        whiteBoardEnabled: true,
        raiseHandEnabled: true,

        recordingEnabled: true,
        recordingWebhookUrl: "https://www.videosdk.live/callback",
        participantCanToggleRecording: true,

        brandingEnabled: true,
        brandLogoURL: "/files/logo.jpg",
        // brandLogoURL: "https://picsum.photos/200",
        brandName: "Amrut Energy",
        poweredBy: false,

        participantCanLeave: true, // if false, leave button won't be visible

        // Live stream meeting to youtube
        livestream: {
            autoStart: true,
            outputs: [
                // {
                //   url: "rtmp://x.rtmp.youtube.com/live2",
                //   streamKey: "<STREAM KEY FROM YOUTUBE>",
                // },
            ],
        },

        permissions: {
            askToJoin: false, // Ask joined participants for entry in meeting
            toggleParticipantMic: true, // Can toggle other participant's mic
            toggleParticipantWebcam: true, // Can toggle other participant's webcam
        },

        joinScreen: {
            visible: true, // Show the join screen ?
            title: meeting_title, // Meeting title
            meetingUrl: meeting_url, // Meeting joining url
        },
    };

    meeting.init(config);

}