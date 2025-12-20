package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/line/line-bot-sdk-go/v7/linebot"
	_ "github.com/mattn/go-sqlite3"
)

var (
	bot *linebot.Client
	db  *sql.DB
)

type Protection struct {
	BadWords      []string
	MutedUsers    map[string]time.Time
	UserMessages  map[string][]time.Time
}

var protection *Protection

func init() {
	protection = &Protection{
		BadWords: []string{
			"غبي", "احمق", "حمار", "كلب", "خنزير", "قذر", "وسخ", "حقير", "نذل",
			"خائن", "كذاب", "لعين", "ملعون", "عاهر", "زاني", "فاسق", "منافق",
		},
		MutedUsers:   make(map[string]time.Time),
		UserMessages: make(map[string][]time.Time),
	}
}

func main() {
	var err error
	
	channelSecret := os.Getenv("LINE_CHANNEL_SECRET")
	channelToken := os.Getenv("LINE_CHANNEL_ACCESS_TOKEN")
	
	if channelSecret == "" || channelToken == "" {
		log.Fatal("يجب تعيين LINE_CHANNEL_SECRET و LINE_CHANNEL_ACCESS_TOKEN")
	}

	bot, err = linebot.New(channelSecret, channelToken)
	if err != nil {
		log.Fatal(err)
	}

	db, err = sql.Open("sqlite3", "./protection.db")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	initDatabase()

	http.HandleFunc("/callback", callbackHandler)
	http.HandleFunc("/health", healthHandler)

	port := os.Getenv("PORT")
	if port == "" {
		port = "5000"
	}

	log.Printf("بدء الخادم على المنفذ %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}

func initDatabase() {
	queries := []string{
		`CREATE TABLE IF NOT EXISTS owners (
			user_id TEXT PRIMARY KEY,
			added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE TABLE IF NOT EXISTS admins (
			user_id TEXT PRIMARY KEY,
			added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE TABLE IF NOT EXISTS banned_users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			group_id TEXT NOT NULL,
			user_id TEXT NOT NULL,
			banned_by TEXT NOT NULL,
			reason TEXT,
			banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(group_id, user_id)
		)`,
		`CREATE TABLE IF NOT EXISTS warnings (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			group_id TEXT NOT NULL,
			user_id TEXT NOT NULL,
			warned_by TEXT NOT NULL,
			reason TEXT,
			warned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE TABLE IF NOT EXISTS groups_settings (
			group_id TEXT PRIMARY KEY,
			links_protection BOOLEAN DEFAULT 1,
			spam_protection BOOLEAN DEFAULT 1,
			flood_protection BOOLEAN DEFAULT 1,
			bad_words_protection BOOLEAN DEFAULT 1,
			welcome_enabled BOOLEAN DEFAULT 1
		)`,
	}

	for _, query := range queries {
		if _, err := db.Exec(query); err != nil {
			log.Printf("خطأ في إنشاء الجدول: %v", err)
		}
	}
	
	log.Println("تم تهيئة قاعدة البيانات")
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "البوت يعمل بشكل صحيح")
}

func callbackHandler(w http.ResponseWriter, r *http.Request) {
	events, err := bot.ParseRequest(r)
	if err != nil {
		if err == linebot.ErrInvalidSignature {
			w.WriteHeader(http.StatusBadRequest)
		} else {
			w.WriteHeader(http.StatusInternalServerError)
		}
		return
	}

	for _, event := range events {
		handleEvent(event)
	}
}

func handleEvent(event *linebot.Event) {
	switch event.Type {
	case linebot.EventTypeMessage:
		handleMessage(event)
	case linebot.EventTypeJoin:
		handleJoin(event)
	case linebot.EventTypeMemberJoined:
		handleMemberJoin(event)
	}
}

func handleMessage(event *linebot.Event) {
	var groupID string
	switch source := event.Source.(type) {
	case *linebot.GroupSource:
		groupID = source.GroupID
	default:
		replyText(event, "هذا البوت يعمل في القروبات فقط")
		return
	}

	message, ok := event.Message.(*linebot.TextMessage)
	if !ok {
		return
	}

	text := strings.TrimSpace(message.Text)
	userID := event.Source.UserID

	isOwner := checkOwner(userID)
	isAdmin := checkAdmin(userID) || isOwner

	if isMuted(groupID, userID) && !isAdmin {
		return
	}

	switch {
	case strings.HasPrefix(text, "اضف مالك"):
		if !isOwner {
			replyText(event, "هذا الامر للمالك فقط")
			return
		}
		mentionedID := extractUserID(text)
		if mentionedID != "" {
			addOwner(mentionedID)
			replyText(event, "تم اضافة المالك بنجاح")
		}

	case strings.HasPrefix(text, "حذف مالك"):
		if !isOwner {
			replyText(event, "هذا الامر للمالك فقط")
			return
		}
		mentionedID := extractUserID(text)
		if mentionedID != "" {
			removeOwner(mentionedID)
			replyText(event, "تم حذف المالك")
		}

	case strings.HasPrefix(text, "اضف ادمن"):
		if !isAdmin {
			replyText(event, "هذا الامر للادمن فقط")
			return
		}
		mentionedID := extractUserID(text)
		if mentionedID != "" {
			addAdmin(mentionedID)
			replyText(event, "تم اضافة الادمن بنجاح")
		}

	case strings.HasPrefix(text, "حذف ادمن"):
		if !isAdmin {
			replyText(event, "هذا الامر للادمن فقط")
			return
		}
		mentionedID := extractUserID(text)
		if mentionedID != "" {
			removeAdmin(mentionedID)
			replyText(event, "تم حذف الادمن")
		}

	case strings.HasPrefix(text, "بان") || strings.HasPrefix(text, "حظر"):
		if !isAdmin {
			replyText(event, "هذا الامر للادمن فقط")
			return
		}
		mentionedID := extractUserID(text)
		if mentionedID != "" {
			if checkAdmin(mentionedID) || checkOwner(mentionedID) {
				replyText(event, "لا يمكن حظر ادمن او مالك")
				return
			}
			parts := strings.Fields(text)
			reason := "مخالفة قوانين القروب"
			if len(parts) > 2 {
				reason = strings.Join(parts[2:], " ")
			}
			banUser(groupID, mentionedID, userID, reason)
			kickUser(groupID, mentionedID)
			replyText(event, fmt.Sprintf("تم حظر المستخدم\nالسبب: %s", reason))
		}

	case strings.HasPrefix(text, "الغاء بان") || strings.HasPrefix(text, "الغاء حظر"):
		if !isAdmin {
			replyText(event, "هذا الامر للادمن فقط")
			return
		}
		mentionedID := extractUserID(text)
		if mentionedID != "" {
			unbanUser(groupID, mentionedID)
			replyText(event, "تم الغاء الحظر")
		}

	case strings.HasPrefix(text, "كتم") || strings.HasPrefix(text, "ميوت"):
		if !isAdmin {
			replyText(event, "هذا الامر للادمن فقط")
			return
		}
		mentionedID := extractUserID(text)
		if mentionedID != "" {
			if checkAdmin(mentionedID) || checkOwner(mentionedID) {
				replyText(event, "لا يمكن كتم ادمن او مالك")
				return
			}
			muteUser(groupID, mentionedID, 30)
			replyText(event, "تم كتم المستخدم لمدة 30 دقيقة")
		}

	case strings.HasPrefix(text, "انذار") || strings.HasPrefix(text, "تحذير"):
		if !isAdmin {
			replyText(event, "هذا الامر للادمن فقط")
			return
		}
		mentionedID := extractUserID(text)
		if mentionedID != "" {
			if checkAdmin(mentionedID) || checkOwner(mentionedID) {
				replyText(event, "لا يمكن انذار ادمن او مالك")
				return
			}
			parts := strings.Fields(text)
			reason := "مخالفة"
			if len(parts) > 2 {
				reason = strings.Join(parts[2:], " ")
			}
			warnings := addWarning(groupID, mentionedID, userID, reason)
			if warnings >= 3 {
				kickUser(groupID, mentionedID)
				replyText(event, fmt.Sprintf("تم طرد المستخدم بعد %d انذارات", warnings))
			} else {
				replyText(event, fmt.Sprintf("تم اعطاء انذار (%d/3)\nالسبب: %s", warnings, reason))
			}
		}

	case strings.HasPrefix(text, "طرد") || strings.HasPrefix(text, "كيك"):
		if !isAdmin {
			replyText(event, "هذا الامر للادمن فقط")
			return
		}
		mentionedID := extractUserID(text)
		if mentionedID != "" {
			if checkAdmin(mentionedID) || checkOwner(mentionedID) {
				replyText(event, "لا يمكن طرد ادمن او مالك")
				return
			}
			kickUser(groupID, mentionedID)
			replyText(event, "تم طرد المستخدم")
		}

	case text == "الاوامر":
		replyText(event, getCommandsList(isAdmin, isOwner))

	case text == "احصائيات":
		if !isAdmin {
			replyText(event, "هذا الامر للادمن فقط")
			return
		}
		stats := getGroupStats(groupID)
		replyText(event, stats)

	default:
		if !isAdmin {
			if checkViolation(groupID, userID, text) {
				return
			}
		}
	}
}

func checkViolation(groupID, userID, text string) bool {
	if checkFlood(groupID, userID) {
		muteUser(groupID, userID, 5)
		pushMessage(groupID, "تم كتم المستخدم بسبب الفلود")
		return true
	}

	if checkLinks(text) {
		addWarning(groupID, userID, "bot", "ارسال روابط")
		pushMessage(groupID, "ممنوع ارسال الروابط")
		return true
	}

	if checkBadWords(text) {
		addWarning(groupID, userID, "bot", "كلمات غير لائقة")
		pushMessage(groupID, "ممنوع الكلمات غير اللائقة")
		return true
	}

	return false
}

func checkFlood(groupID, userID string) bool {
	key := groupID + ":" + userID
	now := time.Now()
	
	messages, exists := protection.UserMessages[key]
	if !exists {
		messages = []time.Time{}
	}

	var recent []time.Time
	for _, t := range messages {
		if now.Sub(t) < 10*time.Second {
			recent = append(recent, t)
		}
	}

	recent = append(recent, now)
	protection.UserMessages[key] = recent

	return len(recent) > 5
}

func checkLinks(text string) bool {
	patterns := []string{
		`http[s]?://`,
		`www\.`,
		`t\.me`,
		`line\.me`,
		`bit\.ly`,
	}

	for _, pattern := range patterns {
		matched, _ := regexp.MatchString(pattern, strings.ToLower(text))
		if matched {
			return true
		}
	}
	return false
}

func checkBadWords(text string) bool {
	text = strings.ToLower(text)
	for _, word := range protection.BadWords {
		if strings.Contains(text, word) {
			return true
		}
	}
	return false
}

func muteUser(groupID, userID string, minutes int) {
	key := groupID + ":" + userID
	protection.MutedUsers[key] = time.Now().Add(time.Duration(minutes) * time.Minute)
}

func isMuted(groupID, userID string) bool {
	key := groupID + ":" + userID
	expiry, exists := protection.MutedUsers[key]
	if !exists {
		return false
	}
	if time.Now().After(expiry) {
		delete(protection.MutedUsers, key)
		return false
	}
	return true
}

func extractUserID(text string) string {
	re := regexp.MustCompile(`U[0-9a-f]{32}`)
	match := re.FindString(text)
	return match
}

func checkOwner(userID string) bool {
	var count int
	db.QueryRow("SELECT COUNT(*) FROM owners WHERE user_id = ?", userID).Scan(&count)
	return count > 0
}

func checkAdmin(userID string) bool {
	var count int
	db.QueryRow("SELECT COUNT(*) FROM admins WHERE user_id = ?", userID).Scan(&count)
	return count > 0
}

func addOwner(userID string) {
	db.Exec("INSERT OR IGNORE INTO owners (user_id) VALUES (?)", userID)
}

func removeOwner(userID string) {
	db.Exec("DELETE FROM owners WHERE user_id = ?", userID)
}

func addAdmin(userID string) {
	db.Exec("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", userID)
}

func removeAdmin(userID string) {
	db.Exec("DELETE FROM admins WHERE user_id = ?", userID)
}

func banUser(groupID, userID, adminID, reason string) {
	db.Exec(`INSERT OR REPLACE INTO banned_users (group_id, user_id, banned_by, reason) 
		VALUES (?, ?, ?, ?)`, groupID, userID, adminID, reason)
}

func unbanUser(groupID, userID string) {
	db.Exec("DELETE FROM banned_users WHERE group_id = ? AND user_id = ?", groupID, userID)
}

func addWarning(groupID, userID, adminID, reason string) int {
	db.Exec(`INSERT INTO warnings (group_id, user_id, warned_by, reason) 
		VALUES (?, ?, ?, ?)`, groupID, userID, adminID, reason)
	
	var count int
	db.QueryRow("SELECT COUNT(*) FROM warnings WHERE group_id = ? AND user_id = ?", 
		groupID, userID).Scan(&count)
	return count
}

func getGroupStats(groupID string) string {
	var banned, warnings int
	db.QueryRow("SELECT COUNT(*) FROM banned_users WHERE group_id = ?", groupID).Scan(&banned)
	db.QueryRow("SELECT COUNT(*) FROM warnings WHERE group_id = ?", groupID).Scan(&warnings)
	
	return fmt.Sprintf("احصائيات القروب\n\nالمحظورين: %d\nالانذارات: %d", banned, warnings)
}

func getCommandsList(isAdmin, isOwner bool) string {
	commands := "قائمة الاوامر\n\n"
	commands += "الاوامر العامة\n"
	commands += "• الاوامر\n"
	commands += "• احصائيات\n"
	
	if isAdmin {
		commands += "\nاوامر الحماية\n"
		commands += "• بان @المستخدم السبب\n"
		commands += "• الغاء بان @المستخدم\n"
		commands += "• كتم @المستخدم\n"
		commands += "• طرد @المستخدم\n"
		commands += "• انذار @المستخدم السبب\n"
	}
	
	if isOwner {
		commands += "\nاوامر المالك\n"
		commands += "• اضف مالك @المستخدم\n"
		commands += "• حذف مالك @المستخدم\n"
		commands += "• اضف ادمن @المستخدم\n"
		commands += "• حذف ادمن @المستخدم\n"
	}
	
	return commands
}

func kickUser(groupID, userID string) {
	if _, err := bot.LeaveGroup(groupID).WithUserID(userID).Do(); err != nil {
		log.Printf("فشل الطرد: %v", err)
	}
}

func handleJoin(event *linebot.Event) {
	var groupID string
	if source, ok := event.Source.(*linebot.GroupSource); ok {
		groupID = source.GroupID
	}
	
	db.Exec("INSERT OR IGNORE INTO groups_settings (group_id) VALUES (?)", groupID)
	
	message := "شكرا لاضافة البوت\nبوت حماية قروبات احترافي\n\nاكتب الاوامر لعرض جميع الاوامر"
	pushMessage(groupID, message)
}

func handleMemberJoin(event *linebot.Event) {
	var groupID string
	if source, ok := event.Source.(*linebot.GroupSource); ok {
		groupID = source.GroupID
	}

	joined := event.Joined
	if joined != nil {
		for _, member := range joined.Members {
			var count int
			db.QueryRow("SELECT COUNT(*) FROM banned_users WHERE group_id = ? AND user_id = ?",
				groupID, member.UserID).Scan(&count)
			
			if count > 0 {
				kickUser(groupID, member.UserID)
				pushMessage(groupID, "تم طرد مستخدم محظور")
			}
		}
	}
}

func replyText(event *linebot.Event, text string) {
	if _, err := bot.ReplyMessage(event.ReplyToken, linebot.NewTextMessage(text)).Do(); err != nil {
		log.Printf("خطأ في الرد: %v", err)
	}
}

func pushMessage(to, text string) {
	if _, err := bot.PushMessage(to, linebot.NewTextMessage(text)).Do(); err != nil {
		log.Printf("خطأ في الارسال: %v", err)
	}
}
