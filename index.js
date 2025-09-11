import express from "express";
import line from "@line/bot-sdk";
import fs from "fs";

const app = express();

// إعدادات LINE
const config = {
  channelAccessToken: process.env.LINE_CHANNEL_ACCESS_TOKEN,
  channelSecret: process.env.LINE_CHANNEL_SECRET,
};

const client = new line.Client(config);

let admins = JSON.parse(fs.readFileSync("admins.json", "utf8"));
let protectedMembers = JSON.parse(fs.readFileSync("protected.json", "utf8"));
let kickLocked = true;

// حفظ البيانات
function saveAdmins() {
  fs.writeFileSync("admins.json", JSON.stringify(admins, null, 2));
}

function saveProtected() {
  fs.writeFileSync("protected.json", JSON.stringify(protectedMembers, null, 2));
}

// Webhook
app.post("/api/webhook", line.middleware(config), (req, res) => {
  Promise.all(req.body.events.map(handleEvent))
    .then((result) => res.json(result))
    .catch((err) => {
      console.error(err);
      res.status(500).end();
    });
});

async function handleEvent(event) {
  if (event.type !== "message" || event.message.type !== "text") {
    return Promise.resolve(null);
  }

  const userId = event.source.userId;
  const text = event.message.text.trim();

  // أوامر الأدمن فقط
  if (admins.includes(userId)) {
    if (text.startsWith("!اضف_ادمن")) {
      const target = text.split(" ")[1];
      if (!admins.includes(target)) {
        admins.push(target);
        saveAdmins();
        return client.replyMessage(event.replyToken, { type: "text", text: "✅ تمت إضافة الأدمن" });
      }
    }

    if (text.startsWith("!حذف_ادمن")) {
      const target = text.split(" ")[1];
      admins = admins.filter(a => a !== target);
      saveAdmins();
      return client.replyMessage(event.replyToken, { type: "text", text: "🗑️ تم حذف الأدمن" });
    }

    if (text === "!الادمنز") {
      return client.replyMessage(event.replyToken, { type: "text", text: `👑 قائمة الأدمنز:\n${admins.join("\n") || "لا يوجد أدمنز"}` });
    }

    if (text === "!قفل_الطرد") {
      kickLocked = true;
      return client.replyMessage(event.replyToken, { type: "text", text: "🔒 تم قفل الطرد (الأدمن فقط يستطيع الطرد)" });
    }

    if (text === "!فتح_الطرد") {
      kickLocked = false;
      return client.replyMessage(event.replyToken, { type: "text", text: "🔓 تم فتح الطرد" });
    }

    if (text.startsWith("!حماية")) {
      const target = text.split(" ")[1];
      if (!protectedMembers.includes(target)) {
        protectedMembers.push(target);
        saveProtected();
        return client.replyMessage(event.replyToken, { type: "text", text: "🛡️ تمت إضافة العضو إلى قائمة المحميين" });
      }
    }

    if (text.startsWith("!الغاء_الحماية")) {
      const target = text.split(" ")[1];
      protectedMembers = protectedMembers.filter(p => p !== target);
      saveProtected();
      return client.replyMessage(event.replyToken, { type: "text", text: "⚠️ تم إزالة العضو من قائمة المحميين" });
    }

    if (text === "!المحميين") {
      return client.replyMessage(event.replyToken, { type: "text", text: `🛡️ قائمة المحميين:\n${protectedMembers.join("\n") || "لا يوجد محميين"}` });
    }
  }

  // رد افتراضي للتأكد أن البوت شغال
  return client.replyMessage(event.replyToken, { type: "text", text: `✅ البوت شغال واستقبل: ${text}` });
}

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
  console.log(`🚀 Bot server running on port ${PORT}`);
});
