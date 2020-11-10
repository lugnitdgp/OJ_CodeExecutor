package OJserver

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"os"
	"strings"
	"sync"

	"github.com/spf13/viper"
)

// FileStore is a cache type of system to store filepaths and hashes
type FileStore struct {
	items map[string]string
	mu    sync.RWMutex
}

// Get returns value of hash / empty string if key exists/doesn't exist and if the key is present or not
func (fs *FileStore) Get(k string) (string, bool) {
	fs.mu.RLock()
	item, found := fs.items[k]
	if !found {
		fs.mu.RUnlock()
		return "", false
	}
	fs.mu.RUnlock()
	return item, true
}

// Set sets the key value pair in filestore using Mutex
func (fs *FileStore) Set(k, i string) {
	fs.mu.Lock()
	fs.items[k] = i
	fs.mu.Unlock()
}

// RequestStore is used to store individual requests made
type RequestStore struct {
	Rid          string   `json:"rid"`
	InputUrls    []string `json:"input_urls"`
	InputHashes  []string `json:"input_hashes"`
	OutputUrls   []string `json:"output_urls"`
	OutputHashes []string `json:"output_hashes"`
	Code         string   `json:"code"`
	Lang         string   `json:"language"`
	TimeLimit    int      `json:"time_limit"`
	MemLimit     int      `json:"mem_limit"`
}

// File Cache Object
var fs FileStore

// Media server URL is of the format: domain/media/testcases/ques_2/test_1/out_sEaSjGI.txt
// Using url as file storage directory excluding domain

// GetPathFromURL formats the download url to a file path
func GetPathFromURL(url string) string {
	return strings.SplitAfterN(url, "/media/", 2)[2]
}

// DownloadFile downloads file also checks for pre-existing file
func DownloadFile(url, filepath string) error {
	// Get the file data
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	dirpath := filepath[0:strings.LastIndex(filepath, "/")]
	if _, err := os.Stat(dirpath); os.IsNotExist(err) {
		// Create the Directory
		err := os.MkdirAll(dirpath, os.ModePerm)
		if err != nil {
			return err
		}
		// Create the File
		out, err := os.Create(filepath)
		if err != nil {
			return err
		}
		defer out.Close()
		_, err = io.Copy(out, resp.Body)
		if err != nil {
			return err
		}
	} else {
		out, err := os.Open(filepath)
		if err != nil {
			return err
		}
		defer out.Close()
		err = out.Truncate(0)
		_, err = io.Copy(out, resp.Body)
		if err != nil {
			return err
		}
	}
	return nil
}

// AcquireFiles downloads i/o files if not found on the server
func (ru *RequestStore) AcquireFiles() {
	for i := 0; i < len(ru.InputUrls); i++ {

		hash, found := fs.Get(ru.InputUrls[i])
		if !found {

			filepath := GetPathFromURL(ru.InputUrls[i])
			DownloadFile(ru.InputUrls[i], filepath)
			fs.Set(ru.InputUrls[i], ru.InputHashes[i])

		} else if hash != ru.InputHashes[i] {

			filepath := GetPathFromURL(ru.InputUrls[i])
			DownloadFile(ru.InputUrls[i], filepath)
			fs.Set(ru.InputUrls[i], ru.InputHashes[i])

		} else {
			continue
		}

		hash, found = fs.Get(ru.OutputUrls[i])
		if !found {

			filepath := GetPathFromURL(ru.OutputUrls[i])
			DownloadFile(ru.OutputUrls[i], filepath)
			fs.Set(ru.OutputUrls[i], ru.OutputHashes[i])

		} else if hash != ru.OutputHashes[i] {

			filepath := GetPathFromURL(ru.InputUrls[i])
			DownloadFile(ru.OutputUrls[i], filepath)
			fs.Set(ru.OutputUrls[i], ru.OutputHashes[i])

		} else {
			continue
		}
	}
	DownloadFile(ru.Code, GetPathFromURL(ru.Code))
}

// RunCode uses safexec to run the code
func (ru *RequestStore) RunCode() {
	// Temp output file
	tempFile, err := ioutil.TempFile("temp", "temp-output-file-*.txt")
	if err != nil {
		return
	}
	defer os.Remove(tempFile.Name())

}

// CodeRunnerHandler handles all requests made to '/coderunner'
func CodeRunnerHandler(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/coderunner" {
		http.Error(w, "404 not found", http.StatusNotFound)
		return
	}

	ip, _, err := net.SplitHostPort(r.RemoteAddr)
	// Checks Client IP address and allows or blocks the request accordingly
	if err != nil {
		log.Fatalln(err)
		return
	} else if ip != viper.Get("client") {
		// Rejected the request
		http.Error(w, "403 Forbidden", http.StatusForbidden)
		fmt.Fprintf(w, "Client IP: %q is not allowed", ip)
		return
	} else {
		// Server has accepted the request
		switch r.Method {
		case "GET":
			http.Error(w, "400 Bad Request", http.StatusBadRequest)
		case "POST":
			var ru RequestStore
			// Decoding JSON body of the POST request
			decoder := json.NewDecoder(r.Body)
			err = decoder.Decode(&ru)
			if err != nil {
				http.Error(w, err.Error(), http.StatusBadRequest)
				return
			}
			ru.AcquireFiles()
			ru.RunCode()
		}
	}
}

func main() {

	viper.SetConfigFile(".env")
	viper.ReadInConfig()

	http.HandleFunc("/coderunner", CodeRunnerHandler)

	fmt.Println("Starting OJ request handler at port: ", viper.Get("port"))

	if err := http.ListenAndServe(":"+viper.Get("port").(string), nil); err != nil {
		log.Fatalln(err)
	}

}
