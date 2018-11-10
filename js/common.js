var language = 'en';
var pathFilm = './';
var playerVideo = '';
var playreVideoParam = '';

function readConfigFile(){
    $.ajax({
        url: "cgi-bin/read_config_file.py",
        data: {
            "file":"./config/config.ini"
        },
        method: 'GET',
        contentType: 'json',
        dataType : "json",
        async: false,
        success: function(data) {
            language = data['language'];
            pathFilm = data['path-film'];
            playerVideo = data['player-video'];
            playreVideoParam = data['player-video-param'];
        },
        error: function(data, status,req){
            alert("source: */readConfigFile() \nerror: " + status + "\n" + req + "\n" );
        }
    });
}
