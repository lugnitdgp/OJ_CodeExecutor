package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"sync"

	"github.com/spf13/viper"
)

var enginePath string
var outpath string

// FileStore is a cache kind of system to store filepaths and hashes
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

// RunnerStatus stores the run status of the request
type RunnerStatus struct {
	code   int
	status map[string]string
}

// File Cache Object
var fs FileStore

// Media server URL is of the format: domain/media/testcases/ques_2/test_1/out_sEaSjGI.txt
// Using url as file storage directory excluding domain

// GetPathFromURL formats the download url to a file path
func GetPathFromURL(url string) string {
	return strings.SplitAfterN(url, "/media/", 2)[1]
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

	return nil
}

// AcquireFiles downloads i/o files if not found locally
func (ru *RequestStore) AcquireFiles() {
	for i := 0; i < len(ru.InputUrls); i++ {

		hash, found := fs.Get(ru.InputUrls[i])
		if !found || hash != ru.InputHashes[i] {
			filepath := GetPathFromURL(ru.InputUrls[i])
			if err := DownloadFile(ru.InputUrls[i], filepath); err == nil {
				fs.Set(ru.InputUrls[i], ru.InputHashes[i])
			}
		}

		hash, found = fs.Get(ru.OutputUrls[i])
		if !found || hash != ru.OutputHashes[i] {
			filepath := GetPathFromURL(ru.OutputUrls[i])
			if err := DownloadFile(ru.OutputUrls[i], filepath); err == nil {
				fs.Set(ru.OutputUrls[i], ru.OutputHashes[i])
			}
		}
	}
	DownloadFile(ru.Code, GetPathFromURL(ru.Code))
}

// CompileCode uses safexec to run the code
func (ru *RequestStore) CompileCode() (RunnerStatus, error) {
	var st RunnerStatus
	st.code = 0
	st.status = map[string]string{}
	// Running compile commands here
	compileCommand := viper.Get(ru.Lang + "_compile")
	compileCommand = fmt.Sprintf(compileCommand.(string), GetPathFromURL(ru.Code))
	cmd := exec.Command("bash", "-c", compileCommand.(string))
	if err := cmd.Run(); err != nil {
		st.code = 1
		st.status["compile_status"] = err.Error()
		return st, err
	}

	compileLog, err := os.Open("compile_log")
	if err != nil {
		st.code = 1
		st.status["compile_status"] = err.Error()
		return st, err
	}
	defer os.Remove(compileLog.Name())

	cl, err := compileLog.Stat()
	if err != nil {
		st.code = 1
		st.status["compile_status"] = err.Error()
		return st, err
	}
	if cl.Size() != 0 {
		st.code = 1
		buf, err := ioutil.ReadFile("compile_log")
		if err != nil {
			st.code = 1
			st.status["compile_status"] = err.Error()
			return st, err
		}
		st.status["compile_status"] = string(buf)
	}
	return st, nil
}

// Format formats the command to fill in all variables
func format(cmd string, params map[string]string) string {
	final := ""
	for i := 0; i < len(cmd); i++ {
		if cmd[i] != '{' {
			final = final + string(cmd[i])
		} else {
			for j := 0; j < len(cmd); j++ {
				if j == '}' {
					varName := cmd[i+1 : j]
					final = final + params[varName]
				}
			}
		}
	}
	return final
}

func status() (map[string]string, error) {
	var tmpStatCmd = "sudo cat usage.txt > temp_stat_file"
	var stat map[string]string
	cmd := exec.Command("bash", "-c", tmpStatCmd)
	if err := cmd.Run(); err != nil {
		return stat, err
	}
	buf, err := ioutil.ReadFile("temp_stat_file")
	if err != nil {
		return stat, err
	}
	f := strings.Split(string(buf), "\n")
	stat["run_status"] = strings.Split(strings.TrimSpace(strings.Split(f[0], ":")[1]), " ")[0]
	stat["elapsed_time"] = strings.Split(strings.TrimSpace(strings.Split(f[1], ":")[1]), " ")[0]
	stat["memory_taken"] = strings.Split(strings.TrimSpace(strings.Split(f[2], ":")[1]), " ")[0]
	stat["cpu_time"] = strings.Split(strings.TrimSpace(strings.Split(f[3], ":")[1]), " ")[0]
	return stat, nil
}

func compare(outFile, tmpOutFile string) bool {
	cmpCode := exec.Command("diff", "-q", outFile, tmpOutFile)
	if err := cmpCode.Run(); err == nil {
		return true
	}
	return false

}

// RunCode executes the code
func (ru *RequestStore) RunCode() ([]RunnerStatus, error) {
	var st RunnerStatus
	st.code = 0
	st.status = nil
	var params map[string]string
	params["enginepath"] = enginePath
	params["outpath"] = outpath
	params["time"] = strconv.Itoa(ru.TimeLimit)
	params["mem"] = strconv.Itoa(ru.MemLimit)
	params["file"] = GetPathFromURL(ru.Code)
	tempFile, err := ioutil.TempFile("temp", "temp-output-file-*.txt")
	if err != nil {
		st.code = 1
		return []RunnerStatus{st}, err
	}
	defer os.Remove(tempFile.Name())
	params["tmpOutFile"] = tempFile.Name()

	var netRes = make([]RunnerStatus, len(ru.InputUrls))
	runCmd := viper.GetString(ru.Lang + "_runcmd")
	for i := 0; i < len(ru.InputUrls); i++ {
		params["inFile"] = GetPathFromURL(ru.InputUrls[i])
		params["outFile"] = GetPathFromURL(ru.OutputUrls[i])
		runCmd := format(runCmd, params)
		cmd := exec.Command("bash", "-c", runCmd)
		var res RunnerStatus
		if err := cmd.Run(); err == nil {
			stat, err := status()
			if err != nil {
				return []RunnerStatus{st}, err
			}
			if stat["run_status"] == "OK" {
				if compare(params["outFile"], params["tmpOutFile"]) {
					stat["run_status"] = "AC"
				} else {
					stat["run_status"] = "WA"
				}
				res.code = 0
				res.status = stat
			} else {
				res.code = 2
				res.status = stat
			}
		} else {
			st.code = 1
			st.status["run_status"] = err.Error()
			return []RunnerStatus{st}, err
		}
		netRes = append(netRes, res)
	}
	return netRes, nil
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
			st, err := ru.CompileCode()
			if err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
			}
			if st.code == 0 {
				netRes, err := ru.RunCode()
				if err != nil {
					http.Error(w, err.Error(), http.StatusInternalServerError)
				} else {
					jsonData, err := json.Marshal(netRes)
					if err != nil {
						http.Error(w, err.Error(), http.StatusInternalServerError)
					}
					w.Header().Set("Content-Type", "application/json")
					w.Write(jsonData)
				}
			} else {
				var res = map[string]string{
					"code":    strconv.Itoa(st.code),
					"message": st.status["compile_status"],
				}
				jsonData, err := json.Marshal(res)
				if err != nil {
					http.Error(w, err.Error(), http.StatusInternalServerError)
				}
				w.Header().Set("Content-Type", "application/json")
				w.Write(jsonData)
			}
		}
	}
}

func main() {

	viper.SetConfigFile(".env")
	viper.ReadInConfig()
	enginePath = viper.GetString("engine_path")
	outpath = viper.GetString("outpath")

	http.HandleFunc("/coderunner", CodeRunnerHandler)

	fmt.Println("Starting OJ request handler at port: ", viper.Get("port"))

	if err := http.ListenAndServe(":"+viper.Get("port").(string), nil); err != nil {
		log.Fatalln(err)
	}

}
