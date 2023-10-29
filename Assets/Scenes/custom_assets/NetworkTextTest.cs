// NetworkTextTest.cs
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System.Text;

public class NetworkTextTest : MonoBehaviour
{
    private string apiUrl = "http://192.168.0.17:8000/chatbot/test_text"; // FastAPI 서버의 엔드포인트 URL을 입력하세요.

    void Start()
    {
        // JSON 데이터 생성
        string json = "{\"text\":\"Text Test Hi!\"}";

        // JSON 데이터를 바이트 배열로 변환
        byte[] jsonData = Encoding.UTF8.GetBytes(json);

        StartCoroutine(PostJson(jsonData));
    }

    IEnumerator PostJson(byte[] jsonData)
    {
        using (UnityWebRequest www = new UnityWebRequest(apiUrl, "POST"))
        {
            www.uploadHandler = new UploadHandlerRaw(jsonData);
            www.downloadHandler = new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError(www.error);
            }
            else
            {
                string responseText = www.downloadHandler.text;
                Debug.Log("Response from server: " + responseText);

                // 여기에서 responseText를 파싱하여 결과값을 추출
            }
        }
    }
}
