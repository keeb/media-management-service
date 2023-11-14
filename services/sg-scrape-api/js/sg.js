// need to set connection as not secure by clicking on lock icon in
// firefox



var i = document.createElement('iframe');
i.style.display = 'none';
document.body.appendChild(i);
window.console = i.contentWindow.console;

var album = document.getElementsByClassName("title")[0].textContent ;
var model = document.getElementsByTagName("title")[0].textContent;
const model_name = model.split("Photo Album")[0].trimStart().trimEnd();
var social = document.getElementById("connected_accounts").getElementsByTagName("a");

var image_section = document.getElementsByClassName("image-section")[0];
var a_tags = image_section.getElementsByTagName("a");

const images = Array();
const socials = Array();


for (var i = 0; i < a_tags.length; i++) {
    var url = a_tags[i].href;
    images.push(url);
}

for (var i = 0; i < social.length; i++) {
    var url = social[i].href;
    socials.push(url);
}

const payload = {};
payload.images = images;
payload.album = album;
payload.model = model_name;
payload.socials = socials;

const submission = JSON.stringify(payload);

fetch("http://treehouse.local:2020",
{
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    },
    method: "POST",
    body: submission,
})
