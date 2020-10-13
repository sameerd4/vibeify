
        var str = '<ul>'
        str += '<tr style="font-weight:bold;font-size:' + (35 + .70 * 100) + '%;"><td>'
        str += ' I am...'
        str += '</td></tr>'

        obj = {{ vibeMoodList | safe }};
        for (var key in obj) {
            if (obj.hasOwnProperty(key)) {
                var val = obj[key];
                str += ''
                switch (key) {
                    case "happyScore":
                        str += '<tr style="font-size:' + (35 + Math.sqrt(val) * 100) + '%;"><td>'
                        str += (val * 100).toFixed(0) + '%'
                        str += ' Happy &#128513;'
                        str += '</td></tr>'
                        break;
                    case "sadScore":
                        str += '<tr style="font-size:' + (35 + Math.sqrt(val) * 100) + '%;"><td>'
                        str += (val * 100).toFixed(0) + '%'
                        str += ' Sadboi &#128532;'
                        str += '</td></tr>'
                        break;
                    case "chillScore":
                        str += '<tr style="font-size:' + (35 + Math.sqrt(val) * 100) + '%;"><td>'
                        str += (val * 100).toFixed(0) + '%'
                        str += ' Chill &#128526;'
                        str += '</td></tr>'
                        break;
                    case "hypeScore":
                        str += '<tr style="font-size:' + (35 + Math.sqrt(val) * 100) + '%;"><td>'
                        str += (val * 100).toFixed(0) + '%'
                        str += ' Hypebeast &#128548;'
                        str += '</td></tr>'
                        break;
                    case "danceScore":
                        str += '<tr style="font-size:' + (35 + Math.sqrt(val) * 100) + '%;"><td>'
                        str += (val * 100).toFixed(0) + '%'
                        str += ' Groovy &#128527;'
                        str += '</td></tr>'
                        break;
                    case "angryScore":
                        str += '<tr style="font-size:' + (35 + Math.sqrt(val) * 100) + '%;"><td>'
                        str += (val * 100).toFixed(0) + '%'
                        str += ' Angry &#128545;'
                        str += '</td></tr>'
                        break;
                }

            }
        }

        str += '</ul>';
        document.getElementById("member_list").innerHTML = str;

        var str3 = '<ul id="menu">'
        obj3 = {{ artistImages | safe }};

        for (var i = 0; i < obj3.length / 2; i++) {
            str3 += '<li>'
            str3 += '<img id="artist-pic" src="' + obj3[i] + '">'
            str3 += '</li>'
        }

        str3 += '</ul>';
        document.getElementById("artist_images").innerHTML = str3;

        var str4 = '<ul id="menu">'

        for (var i = 5; i < obj3.length; i++) {
            str4 += '<li>'
            str4 += '<img id="artist-pic" src="' + obj3[i] + '">'
            str4 += '</li>'
        }

        str4 += '</ul>';
        document.getElementById("artist_images2").innerHTML = str4;

        tracks = {{ favorite_tracks | safe }}
        str2 = '<ul>';
        for (var key in tracks) {
            if (tracks.hasOwnProperty(key)) {
                var val = tracks[key];
                str2 += ''
                switch (key) {
                    case "happy":
                        str2 += '<tr><td id="song-list">Happy &#128513;</td>'
                        str2 += '<td id="cover-art"><image id="album-cover" src="' + val[2] + '" /></td>'
                        str2 += '<td id="track-details"><table style="font-size:50%;"><tbody><tr><td style="font-weight: bold;">' + val[0] + '</td></tr><tr><td>' + val[1] + '</td></tr></tbody></table></td>'
                        str2 += '</tr>'
                        break;
                    case "sad":
                        str2 += '<tr><td id="song-list">Sad &#128532;</td>'
                        str2 += '<td id="cover-art"><image id="album-cover" src="' + val[2] + '" /></td>'
                        str2 += '<td id="track-details"><table style="font-size:50%;"><tbody><tr><td style="font-weight: bold;">' + val[0] + '</td></tr><tr><td>' + val[1] + '</td></tr></tbody></table></td>'
                        str2 += '</tr>'
                        break;
                    case "chill":
                        str2 += '<tr><td id="song-list">Chill &#128526;</td>'
                        str2 += '<td><image id="album-cover" src="' + val[2] + '" /></td>'
                        str2 += '<td id="track-details"><table style="font-size:50%;"><tbody><tr><td style="font-weight: bold;">' + val[0] + '</td></tr><tr><td>' + val[1] + '</td></tr></tbody></table></td>'
                        str2 += '</tr>'
                        break;
                    case "hype":
                        str2 += '<tr><td id="song-list">Hype &#128548;</td>'
                        str2 += '<td><image id="album-cover" src="' + val[2] + '" /></td>'
                        str2 += '<td id="track-details"><table style="font-size:50%;"><tbody><tr><td style="font-weight: bold;">' + val[0] + '</td></tr><tr><td>' + val[1] + '</td></tr></tbody></table></td>'
                        str2 += '</tr>'
                        break;
                    case "dance":
                        str2 += '<tr><td id="song-list">Groovy &#128527;</td>'
                        str2 += '<td><image id="album-cover" src="' + val[2] + '" /></td>'
                        str2 += '<td id="track-details"><table style="font-size:50%;"><tbody><tr><td style="font-weight: bold;">' + val[0] + '</td></tr><tr><td>' + val[1] + '</td></tr></tbody></table></td>'
                        str2 += '</tr>'
                        break;
                    case "angry":
                        str2 += '<tr><td id="song-list">Angry &#128545;</td>'
                        str2 += '<td><image id="album-cover" src="' + val[2] + '" /></td>'
                        str2 += '<td id="track-details"><table style="font-size:50%;"><tbody><tr><td style="font-weight: bold;">' + val[0] + '</td></tr><tr><td>' + val[1] + '</td></tr></tbody></table></td>'
                        str2 += '</tr>'
                        break;
                }

            }
        }

        str2 += '</ul>'
        //        console.log(str2);
        document.getElementById("tracks").innerHTML = str2;

        document.getElementById('download').addEventListener('click', function () {
            var offScreen = document.querySelector('.myVibes_image'), value = offScreen.value;
            offScreen.style.backgroundImage = 'url(/static/background.png)';
            window.scrollTo(0, 0);
            // Use clone with htm2canvas and delete clone
            html2canvas(offScreen, {
                useCORS: true, //By passing this option in function Cross origin images will be rendered properly in the downloaded version of the PDF
                onrendered: function (canvas) {
                    //your functions here
                }
            }).then((canvas) => {
                if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
                    window.open().document.write('<img src="' + canvas.toDataURL() + '" style="width: 90%;display: block;margin-left: auto;margin-right: auto;margin-top: 10%;" />');
                }
                else {
                    var dataURL = canvas.toDataURL();
                    console.log(dataURL);
                    var link = document.createElement('a');
                    link.download = 'spot_my_vibe.png';
                    link.href = dataURL;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    delete link;

                }
            });

            offScreen.style.backgroundImage = '';

        });

        document.getElementById('download2').addEventListener('click', function () {
            var offScreen = document.querySelector('.stat_image'), value = offScreen.value;

//            offScreen.style.backgroundColor = '#B34233';
            offScreen.style.backgroundImage = 'url(/static/background.png)';
            window.scrollTo(0, 0);
            // Use clone with htm2canvas and delete clone
            html2canvas(offScreen, {
                useCORS: true, //By passing this option in function Cross origin images will be rendered properly in the downloaded version of the PDF
                onrendered: function (canvas) {
                    //your functions here
                }
            }).then((canvas) => {
                if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
                    window.open().document.write('<img src="' + canvas.toDataURL() + '" style="width: 90%;display: block;margin-left: auto;margin-right: auto;margin-top: 10%;" />');
                }
                else {
                    var dataURL = canvas.toDataURL();
                    console.log(dataURL);
                    var link = document.createElement('a');
                    link.download = 'spot_my_vibe_stats.png';
                    link.href = dataURL;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    delete link;

                }
            });

            offScreen.style.backgroundImage = '';
        });
